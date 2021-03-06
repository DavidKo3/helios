#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pyhelios_argparser

# Configure runpath from within pyhelios.
helios_run_path = 'run2/'

# Add run path to python path.
sys.path.append(helios_run_path)

# PyHelios import only now possible.
import pyhelios

# Empty list for trajectory values and/or measurement values
tpoints = []
mpoints = []


# Define callback function to continuously extract trajectory values from simulation in case of live plotting.
def live_plotting_callback(output=None):
    global tpoints

    # Store trajectories in variable.
    trajectories = output.trajectories

    # Add current values to list
    try:
        tpoints.append([trajectories[len(trajectories) - 1].getPosition().x,
                        trajectories[len(trajectories) - 1].getPosition().y,
                        trajectories[len(trajectories) - 1].getPosition().z])

    except Exception:
        pass


# Define callback function to continuously extract measurement values from simulation in case of live plotting.
def live_plotting_callback_full(output=None):
    global mpoints

    # Extract measurement points.
    measurements = output.measurements
    if len(measurements) == 0:
        return

    # Add current values to list.
    try:
        mpoints.append([measurements[len(measurements) - 1].getPosition().x,
                        measurements[len(measurements) - 1].getPosition().y,
                        measurements[len(measurements) - 1].getPosition().z,
                        int(measurements[len(measurements) - 1].hitObjectId)])

    except Exception as err:
        print(err)
        pass


def update_3dline(dynamic_list, line_obj, refresh_rate=0.5):
    '''Continuously updates matplotlib line with values from a steadily growing list.
     The function terminates when no new values are added to the list within the specified refresh rate.

    Parameters:
    dynamic_list (list): A continuously growing list of xyz points. Format: [[x, y, z], [x, y, z], ...]).
    line_obj (matplotlib.axes.Axes.plot): An empty line with 3 dimensions. E.g.: l, = ax.plot([], [], []).
    figure (matplotlib.pyplot.figure): The figure which contains the axis used to the create line object.

    Optional:
    refresh_rate (float, default=0.5): Determines time interval in seconds between each iteration of function.
    '''
    loop_stopper = 0
    while True:
        time.sleep(float(refresh_rate))

        # Check whether list contains more new values.
        if loop_stopper != len(dynamic_list):

            # Convert x, y, z list to array.
            a = np.array(dynamic_list)

            # Update values of line with data from array.
            line_obj.set_xdata(a[:, 0])
            line_obj.set_ydata(a[:, 1])
            line_obj.set_3d_properties(zs=a[:, 2])

            # Draw results onto figure.
            plt.draw()
            plt.pause(1e-17)
        else:
            break
        # Variable used to check for updates to list.
        loop_stopper = len(dynamic_list)


# ---  M A I N  --- #
# ----------------- #
if __name__ == '__main__':

    # Parse arguments.
    args = pyhelios_argparser.args

    # Perform test to check whether PyHelios is properly configured and installed.
    if args.test_is_desired:
        print('PyHelios is installed correctly.')
        print('PyHelios version: ' + pyhelios.getVersion())
        exit()

    # Set logging style.
    if args.loggingv:
        pyhelios.loggingVerbose()

    elif args.loggingv2:
        pyhelios.loggingVerbose2()

    elif args.loggingquiet:
        pyhelios.loggingQuiet()

    elif args.loggingsilent:
        pyhelios.loggingSilent()

    else:
        pyhelios.loggingDefault()

    # Set random generator seed if value has been supplied.
    if args.randomness_seed:
        pyhelios.setDefaultRandomnessGeneratorSeed(args.randomness_seed)

    # Initiate a simulation. Parameters: (surveyPath, assetsPath, outputPath, ...).
    sim = pyhelios.Simulation(
        args.survey_file,
        args.assets_path,
        args.output_path,
        args.number_of_threads,  # Num Threads
        args.las_output_flag,  # LAS output
        args.zip_output_flag,  # ZIP output
    )

    # Load the survey file.
    sim.loadSurvey(
        args.leg_noise_disabled_flag,  # Leg Noise Disabled FLAG
        args.rebuild_scene_flag,  # Rebuild Scene FLAG
        args.write_waveform_flag,  # Write Waveform FLAG
        args.calc_echowidth_flag,  # Calculate Echowidth FLAG
        args.fullwave_noise_flag,  # Full Wave Noise FLAG
        args.platform_noise_disabled_flag  # Platform Noise Disabled FLAG
    )

    if not args.live_trajectory_plot and not args.open3d:
        sim.start()

        output = sim.join()

    if args.live_trajectory_plot:
        import time
        import matplotlib.pyplot as plt
        import matplotlib
        from mpl_toolkits.mplot3d import Axes3D, art3d
        import numpy as np

        # Set callback and callback frequency.
        sim.simFrequency = 10000
        sim.setCallback(live_plotting_callback)

        # Empty list for groundplane vals.
        groundplane_list = []

        # List filled every 25th value from (-75, -75, 0) to (75, 75, 0).
        for i in range(-75, 76, 25):
            for j in range(-75, 76, 25):
                groundplane_list.append([i, j, 0])

        # List converted to numpy Array.
        groundplane = np.array(groundplane_list)

        # Matplotlib figure.
        fig = plt.figure()

        # Axes3d axis onto mpl figure.
        ax = fig.add_subplot(111, projection='3d')

        # Set axis extent.
        ax.set_xlim([-75, 75])
        ax.set_ylim([-75, 75])
        ax.set_zlim([0, 100])

        # Add axis labels.
        ax.set_xlabel('$X$')
        ax.set_ylabel('$Y$')
        ax.set_zlabel('$Z$')

        # Set title.
        ax.text2D(0.185, 1, "LIVE:", fontsize='11', transform=ax.transAxes, c='r')
        ax.text2D(0.27, 1, 'PyHelios LiDAR Simulation Trajectory Plot', fontsize='11', transform=ax.transAxes)

        # Plot groundplane onto figure.
        ax.plot_trisurf(groundplane[:, 0], groundplane[:, 1], groundplane[:, 2], color='darkgoldenrod',
                        label='groundplane', alpha=0.5)

        # Update canvas.
        plt.draw()
        plt.pause(1e-17)

        sim.start()

        time.sleep(2)

        # Create empty line object.
        line1, = ax.plot([], [], [])

        # Run function to plot trajectory while simulation is running.
        update_3dline(tpoints, line1, refresh_rate=1)

        output = sim.join()

        plt.show()

    if args.open3d:
        import open3d as o3d
        import numpy as np
        import time
        import matplotlib.pyplot as plt
        import xml.etree.ElementTree as ET

        # Set callback function which retrieves measurement values.
        sim.setCallback(live_plotting_callback_full)
        sim.simFrequency = 10

        # Create point cloud geometry for survey data.
        measurement = o3d.geometry.PointCloud()

        # Parse survey file to extract scene file and then parse the scene file.
        scene = ET.parse(ET.parse(args.survey_file).find('survey').attrib['scene'].split('#')[0])

        # Access XML root of scene file.
        root = scene.getroot()

        # Extract scene data from XML.
        # Create a list and fill it with a series of dicts with data on each individual scene part.
        scene_parts = []
        for scene_part in root.find('scene'):

            scene_part_data = {}

            for filter in scene_part.findall('filter'):
                # --------------------------------------------------------------------------
                # Wavefront scenepart.
                # --------------------------------------------------------------------------
                if filter.attrib['type'] == 'objloader':
                    scene_part_data['extension'] = '.obj'
                    scene_part_data['filepath'] = filter.find('param').attrib['value']

                if filter.attrib['type'] == 'scale':
                    scene_part_data['scale'] = float(filter.find('param').attrib['value'])

                # --------------------------------------------------------------------------
                # Point cloud scenepart.
                # --------------------------------------------------------------------------
                if filter.attrib['type'] == 'xyzloader':
                    scene_part_data['extension'] = '.xyz'

                    for param in filter.findall('param'):
                        if param.attrib['key'] == 'filepath':
                            scene_part_data['filepath'] = param.attrib['value']

                        if param.attrib['key'] == 'voxelSize':
                            scene_part_data['voxelsize'] = float(param.attrib['value'])

                # Translate filter for point clouds.
                if filter.attrib['type'] == 'translate':
                    scene_part_data['translation'] = filter.find('param').attrib['value'].split(';')

            scene_parts.append(scene_part_data)

        # Create instance of visualizer class. Needed for creation of GUI.
        vis = o3d.visualization.Visualizer()
        vis.create_window(window_name="PyHelios Simulation")

        # Add measurement point cloud to window.
        vis.add_geometry(measurement)

        # Loop over scene parts and create individual open3d geometries. Also add the geometries to window.
        # .obj-dict = {extension : '.obj', file_path : str, scale : float, geometry : (o3d_triangle_mesh)}
        # .xyz-dict = {extension : '.xyz', file_path : str, translation : [x, y ,z], voxelsize : float,
        # geometry : (o3d_point_cloud/VoxelGrid)}
        for scene_part in scene_parts:

            if scene_part['extension'] == '.obj':
                # Create open3d object.
                scene_part['geometry'] = (o3d.io.read_triangle_mesh(scene_part['filepath']))

                # Change colour of first scene part. This should be the ground plane.
                if scene_parts.index(scene_part) == 0:
                    scene_part['geometry'].paint_uniform_color([0.866, 0.858, 0.792])

                # Apply translation.
                if 'translation' in scene_part:
                    scene_part['geometry'].translate(np.array(scene_part['translation']))

                # Apply scaling.
                if scene_part['scale'] != 1:
                    scene_part['geometry'].scale(scene_part['scale'], [0, 0, 0])

                # Add geometry to visualizer.
                vis.add_geometry(scene_part['geometry'])

            elif scene_part['extension'] == '.xyz':
                # Create o3d point cloud.
                scene_part['geometry'] = (o3d.io.read_point_cloud(scene_part['filepath']))

                if 'translation' in scene_part:
                    # Translate point cloud.
                    # Get points as np array
                    point_cloud = np.asarray(scene_part['geometry'].points)

                    # Apply translation.
                    point_cloud[:, 0] += float(scene_part['translation'][0])
                    point_cloud[:, 1] += float(scene_part['translation'][1])
                    point_cloud[:, 2] += float(scene_part['translation'][2])

                    # Update geometry points with new values.
                    scene_part['geometry'].points = o3d.utility.Vector3dVector(point_cloud)

                # Set random colours.
                scene_part['geometry'].colors = o3d.utility.Vector3dVector(
                    np.random.uniform(0, 1, size=(point_cloud.shape[0], 3)))

                # Voxelise.
                scene_part['geometry'] = o3d.geometry.VoxelGrid.create_from_point_cloud(scene_part['geometry'],
                                                                                        voxel_size=scene_part['voxelsize'])

                # Add voxels to visualizer.
                vis.add_geometry(scene_part['geometry'])

        # Start pyhelios simulation.
        sim.start()

        while sim.isRunning():
            if len(mpoints) > 0:
                # Convert x, y, z lists with points from pyhelios callback to arrays.
                a = np.array(mpoints)
                # Update o3d point clouds with points from callback.
                measurement.points = o3d.utility.Vector3dVector(a[:, :-1])

                colours = np.zeros((a.shape[0], 3))

                # Set unique colour for each object based on object id.
                obj_ids = a[:, -1]

                uid = np.unique(obj_ids)

                cm = plt.get_cmap('tab10')

                for oid in uid:
                    colours[obj_ids == oid, :] = cm(((oid+1)/15)%1)[:3]  # 15 colors in this colormap, then repeat

                measurement.colors = o3d.utility.Vector3dVector(colours)

                # Update geometries for visualizer.
                vis.update_geometry(measurement)

                # Refresh GUI.
                vis.poll_events()
                vis.update_renderer()

            print('running')

            time.sleep(0.1)

        # Save final output in variable.
        output = sim.join()

        # Keep window open after sim.
        vis.run()

    if args.plot_result:
        # PyHeliostools.
        from pyheliostools import outputToNumpy
        # Polyscope.
        import polyscope as ps

        print('Preparing data for polyscope plot...')

        # Create numpy Array with points from trajectory.
        measurement_points, trajectory_points = outputToNumpy(output)

        # Points to be plotted:
        # First three cols are x, y and z vals.
        t_points = trajectory_points[:, 0:3]
        m_points = measurement_points[:, :3]

        # Initialize polyscope.
        ps.init()

        # Set correct direction for visualization of point clouds.
        ps.set_up_dir("z_up")

        # Register both the trajectory and measurement point clouds seperately.
        measurement_cloud = ps.register_point_cloud("Measurements", m_points)
        trajectory_cloud = ps.register_point_cloud("Scanner Trajectory", t_points)

        # Set more visually appealing point radiuses.
        measurement_cloud.set_radius(0.00091, relative=True)
        trajectory_cloud.set_radius(0.00191, relative=True)

        ps.show()