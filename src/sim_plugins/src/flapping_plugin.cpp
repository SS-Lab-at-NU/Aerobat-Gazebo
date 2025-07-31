#include <gazebo/common/Plugin.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/gazebo.hh>
#include <ros/ros.h>
#include <std_msgs/Float32.h>
#include <std_msgs/Bool.h>

namespace gazebo {

class FlappingPlugin : public ModelPlugin {
public:
  void Load(physics::ModelPtr model, sdf::ElementPtr sdf) override {
    this->model = model;
    joint_name = sdf->Get<std::string>("joint_name");
    amplitude = sdf->Get<double>("amplitude");
    frequency = sdf->Get<double>("frequency");
    z_amplitude = sdf->Get<double>("z_amplitude");
    z_frequency = sdf->Get<double>("z_frequency");

    joint = model->GetJoint(joint_name);
    if (!joint) {
      gzerr << "[FlappingPlugin] Could not find joint: " << joint_name << "\n";
      return;
    }

    // Initialize ROS node
    if (!ros::isInitialized()) {
      int argc = 0;
      char** argv = nullptr;
      ros::init(argc, argv, "flapping_plugin", ros::init_options::NoSigintHandler);
    }
    ros_node.reset(new ros::NodeHandle("flapping_plugin"));

    // ROS subscribers
    frequency_sub = ros_node->subscribe("/flap_frequency", 10, &FlappingPlugin::SetFrequency, this);
    amplitude_sub = ros_node->subscribe("/flap_amplitude", 10, &FlappingPlugin::SetAmplitude, this);
    oscillation_sub = ros_node->subscribe("/flap_oscillation", 10, &FlappingPlugin::SetOscillation, this);
    z_amplitude_sub = ros_node->subscribe("/z_amplitude", 10, &FlappingPlugin::SetZAmplitude, this);
    z_frequency_sub = ros_node->subscribe("/z_frequency", 10, &FlappingPlugin::SetZFrequency, this);

    last_update_time = model->GetWorld()->SimTime();
    update_connection = event::Events::ConnectWorldUpdateBegin(
      std::bind(&FlappingPlugin::OnUpdate, this));
  }

  void OnUpdate() {
    if (!oscillating) return; // Stop oscillation if disabled

    common::Time now = model->GetWorld()->SimTime();
    double dt = (now - last_update_time).Double();
    time_accumulator += dt;

    // Flapping motion (joint oscillation)
    double pos = amplitude * sin(2 * M_PI * frequency * time_accumulator);
    joint->SetPosition(0, pos);

    // Z-axis vibration (model vertical motion)
    double z_pos = z_amplitude * sin(2 * M_PI * z_frequency * time_accumulator);
    auto model_pose = model->WorldPose();
    model_pose.Pos().Z() = z_pos; // Update Z position
    model->SetWorldPose(model_pose);

    last_update_time = now;
  }

  void SetFrequency(const std_msgs::Float32::ConstPtr& msg) {
    this->frequency = msg->data;
  }

  void SetAmplitude(const std_msgs::Float32::ConstPtr& msg) {
    this->amplitude = msg->data;
  }

  void SetOscillation(const std_msgs::Bool::ConstPtr& msg) {
    this->oscillating = msg->data;
  }

  void SetZAmplitude(const std_msgs::Float32::ConstPtr& msg) {
    this->z_amplitude = msg->data;
  }

  void SetZFrequency(const std_msgs::Float32::ConstPtr& msg) {
    this->z_frequency = msg->data;
  }

private:
  physics::ModelPtr model;
  physics::JointPtr joint;
  std::string joint_name;
  double amplitude = 0.5;
  double frequency = 2.0;
  double z_amplitude = 0.1; // Default Z-axis amplitude
  double z_frequency = 1.0; // Default Z-axis frequency
  double time_accumulator = 0.0;
  bool oscillating = false; // Start with oscillation disabled
  common::Time last_update_time;
  event::ConnectionPtr update_connection;

  std::unique_ptr<ros::NodeHandle> ros_node;
  ros::Subscriber frequency_sub;
  ros::Subscriber amplitude_sub;
  ros::Subscriber oscillation_sub;
  ros::Subscriber z_amplitude_sub;
  ros::Subscriber z_frequency_sub;
};

GZ_REGISTER_MODEL_PLUGIN(FlappingPlugin)

}  // namespace gazebo