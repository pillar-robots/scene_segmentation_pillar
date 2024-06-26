#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import rospkg
import os, sys

# Initialize rospkg to find packages
rospack = rospkg.RosPack()
package_path = rospack.get_path('scene_segmentation_pillar')
scene_segmentation_path = os.path.join(package_path, 'scripts')
sys.path.append(scene_segmentation_path)
from scene_segmentation import SceneSegmenterNode


class SceneSegmenterNode(object):
    def __init__(self):
        rospy.init_node('face_tracker_node')
        
        # Initialize the CvBridge and FaceTracker
        self.bridge = CvBridge()
        self.scene_segmenter = SceneSegmenterNode()
        
        # Subscribe to the input video feed and publish annotated images
        self.image_sub = rospy.Subscriber('/xtion/rgb/image_raw', Image, self.image_callback)
        self.image_pub = rospy.Publisher('/scene_segmentation/image', Image, queue_size=10)

    def image_callback(self, data):
        try:
            # Convert the ROS image message to a CV2 image
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            rospy.logerr(e)

        # Perform scene segmentation on the converted CV2 image
        results = self.scene_segmenter.track(cv_image, verbose=False)
        for result in results:
            rospy.loginfo("Boxes: %s", result.boxes)
            rospy.loginfo("Masks: %s", result.masks)

        # Optionally, to publish the result as a ROS Image message
        # Annotate `cv_image` here if you want to visualize the tracking results
        # Then convert it back to a ROS Image message and publish it
        try:
            ros_image = self.bridge.cv2_to_imgmsg(cv_image, "bgr8")
            self.image_pub.publish(ros_image)
        except CvBridgeError as e:
            rospy.logerr(e)

if __name__ == '__main__':
    node = SceneSegmenterNode()
    rospy.spin()
