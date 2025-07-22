#!/bin/bash

# Backup the current file
cp cave_world.mtl cave_world.mtl.backup2

# Replace all Cave_Ground materials with brighter, more detailed texture
sed -i '/newmtl.*Cave_Ground/,/^newmtl\|^$/{
    s/Kd 0.27 0.20 0.16/Kd 0.50 0.40 0.30/
    s/Kd 0.00 0.00 0.00/Kd 0.50 0.40 0.30/
    s/Ka 0.27 0.20 0.16/Ka 0.80 0.80 0.80/
    s/Ka 0.59 0.59 0.59/Ka 0.80 0.80 0.80/
    s/Ni 1.50/Ni 1.00/
    s/Ns 10.00/Ns 0.00/
    /map_Kd/d
    /Tf 1.00 1.00 1.00/a\
map_Kd StriatedRock_Albedo.png
}' cave_world.mtl

# Replace all Cave_Walls materials with brighter, more detailed texture
sed -i '/newmtl.*Cave_Walls/,/^newmtl\|^$/{
    s/Kd 0.13 0.09 0.07/Kd 0.60 0.50 0.40/
    s/Kd 0.00 0.00 0.00/Kd 0.60 0.50 0.40/
    s/Ka 0.13 0.09 0.07/Ka 0.90 0.90 0.90/
    s/Ka 0.59 0.59 0.59/Ka 0.90 0.90 0.90/
    s/Ni 1.50/Ni 1.00/
    s/Ns 10.00/Ns 0.00/
    /map_Kd/d
    /Tf 1.00 1.00 1.00/a\
map_Kd CaveWall_Albedo.png
}' cave_world.mtl

echo "Materials updated with brighter settings"

