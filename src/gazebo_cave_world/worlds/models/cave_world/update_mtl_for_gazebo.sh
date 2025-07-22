#!/bin/bash

# Backup the original file
cp meshes/cave_world.mtl meshes/cave_world.mtl.backup_original

# Replace all Cave_Ground materials to reference Gazebo material
sed -i '/newmtl.*Cave_Ground/,/^newmtl\|^$/{
    /newmtl.*Cave_Ground/!{
        /^newmtl\|^$/!d
    }
    /newmtl.*Cave_Ground/a\
illum 4\
Kd 0.80 0.70 0.60\
Ka 0.60 0.50 0.40\
Tf 1.00 1.00 1.00\
Ni 1.00\
Ks 0.10 0.10 0.10\
Ns 0.00
}' meshes/cave_world.mtl

# Replace all Cave_Walls materials to reference Gazebo material  
sed -i '/newmtl.*Cave_Walls/,/^newmtl\|^$/{
    /newmtl.*Cave_Walls/!{
        /^newmtl\|^$/!d
    }
    /newmtl.*Cave_Walls/a\
illum 4\
Kd 0.70 0.60 0.50\
Ka 0.50 0.40 0.30\
Tf 1.00 1.00 1.00\
Ni 1.00\
Ks 0.10 0.10 0.10\
Ns 0.00
}' meshes/cave_world.mtl

echo "MTL file updated for Gazebo materials"
