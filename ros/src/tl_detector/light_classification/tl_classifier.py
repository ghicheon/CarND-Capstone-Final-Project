#from styx_msgs.msg import TrafficLight

import os
import sys
from glob import glob
from PIL import Image
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from collections import defaultdict
from utils import label_map_util
from utils import visualization_utils as vis_util
import random
from styx_msgs.msg import TrafficLightArray, TrafficLight

## load SSD trained on udacity's simulator images
PATH_TO_GRAPH = r'./light_classification/model/sim/8_batch/frozen_inference_graph.pb' 

PATH_TO_LABELS = r'./light_classification/model/label_map.pbtxt'
NUM_CLASSES = 13

#if the score is under this value, unknown state is returned.
MINIMUM_SCORE_THRESHOLD =0.2

# red in .pb output
RED_LIGHT=1


# .pb file
#subfolder = ['Green', 'Red', 'Yellow', 'Unknown']

#styx_msgs/msg/TrafficLight.msg
#uint8 UNKNOWN=4
#uint8 GREEN=2
#uint8 YELLOW=1
#uint8 RED=0

# .pb -> msg
#convertedColor=[2,0,1,4]

class TLClassifier(object):
    def __init__(self):
        detection_graph = self.load_graph(PATH_TO_GRAPH)
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(
                              label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        category_index = label_map_util.create_category_index(categories)
        print(category_index)
        detection_graph.as_default()

        self.sess = tf.Session(graph= detection_graph)

        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        self.detect_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        self.detect_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.detect_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    def get_classification(self, image):
        """Determines the color of the traffic light in the image

        Args:
            image (cv::Mat): image containing the traffic light

        Returns:
            int: ID of traffic light color (specified in styx_msgs/TrafficLight)

        """
        #TODO implement light color prediction
        #image_np = self.load_image_into_numpy_array(image)
        global MINIMUM_SCORE_THRESHOLD
        global RED_LIGHT
        image_np = image
        image_expanded = np.expand_dims(image_np, axis=0)

        (boxes, scores, classes, num) = self.sess.run(
                                        [self.detect_boxes, self.detect_scores, self.detect_classes, self.num_detections],
                                        feed_dict={self.image_tensor: image_expanded})

       # print('SCORES')
       # print(scores[0])
       # print('CLASSES')
       # print(classes[0])


        #sys.stderr.write("score:classes:  " + str(scores[0]) + "--------" + str(classes[0]) + "\n" )

        if scores[0][0] > MINIMUM_SCORE_THRESHOLD and int(classes[0][0]) == RED_LIGHT :  # 1 is RED in .pb 
                sys.stderr.write("[RED] detected..." + "\n")
                return TrafficLight.RED
        else:
                sys.stderr.write("[^RED] detected..." + "\n")
                return TrafficLight.UNKNOWN



    def load_graph(self,graph_file):
        """Loads a frozen inference graph"""
        graph = tf.Graph()
        with graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(graph_file, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
        return graph
    
    
    def load_image_into_numpy_array(self,image):
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)



        


