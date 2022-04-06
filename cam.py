import pyrealsense2 as rs
import keyboard as kb
import numpy as np
import cv2 as cv
import time

# Alpha value for converting depth info to colourmap
gerandalpha = 0.195

# Print user manual
print('Press [Esc] to exit, [D] for taking depth image, [F] for taking rgb photo.')

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

#######################################################################

# Start streaming
pipeline.start(config)

try:
    depth_index = 0
    colour_index = 0
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv.applyColorMap(cv.convertScaleAbs(depth_image, alpha=gerandalpha), cv.COLORMAP_JET)

        #concatanate image Vertically
        img_concate_Verti=np.concatenate((depth_colormap,color_image),axis=0)

        # Show video stream
        cv.imshow("Output",img_concate_Verti)
        cv.waitKey(0)

        # Take depth photo and save to a jpg image
        if kb.is_pressed('D'):  # if key 'D' is pressed
            filename = 'depth'+str(depth_index)+'.jpg'
            cv.imwrite(filename, depth_colormap)
            print('Saved to '+filename+'!')
            depth_index=depth_index+1
            time.sleep(0.1)

        # Take colour photo and save to a jpg image
        if kb.is_pressed('F'):  # if key 'F' is pressed
            filename = 'rgb'+str(colour_index)+'.jpg'
            cv.imwrite(filename, color_image)
            print('Saved to '+filename+'!')
            colour_index=colour_index+1
            time.sleep(0.1)

        # Stop program
        if kb.is_pressed('Esc'):  # if key 'Esc' is pressed
            print('Exiting...')
            break  # finishing the loop

finally:
    # Stop streaming
    pipeline.stop()
