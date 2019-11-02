from styx_msgs.msg import TrafficLight
import numpy as np
import tensorflow as tf
import os

def filter_boxes(min_score, boxes, scores, classes):
    """Return boxes with a confidence >= `min_score`"""
    n = len(classes)
    idxs = []
    for i in range(n):
        if scores[i] >= min_score:
            idxs.append(i)

    filtered_boxes = boxes[idxs, ...]
    filtered_scores = scores[idxs, ...]
    filtered_classes = classes[idxs, ...]
    return filtered_boxes, filtered_scores, filtered_classes

def to_image_coords(boxes, height, width):
    """
    The original box coordinate output is normalized, i.e [0, 1].

    This converts it back to the original coordinate based on the image
    size.
    """
    box_coords = np.zeros_like(boxes)
    box_coords[:, 0] = boxes[:, 0] * height
    box_coords[:, 1] = boxes[:, 1] * width
    box_coords[:, 2] = boxes[:, 2] * height
    box_coords[:, 3] = boxes[:, 3] * width

    return box_coords

def draw_boxes(image, boxes, classes, thickness=4):
    """Draw bounding boxes on the image"""
    draw = ImageDraw.Draw(image)
    for i in range(len(boxes)):
        bot, left, top, right = boxes[i, ...]
        class_id = int(classes[i])
        color = COLOR_LIST[class_id]
        draw.line([(left, top), (left, bot), (right, bot), (right, top), (left, top)], width=thickness, fill=color)

def load_graph(graph_file):
    """Loads a frozen inference graph"""
    graph = tf.Graph()
    with graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(graph_file, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    return graph

label_map = {1:'green', 2:'red', 3:'yellow', 4:'unknown'}
class TLClassifier(object):

    def __init__(self, is_simulator):

        if is_simulator:
            GRAPH_FILE = 'model/simulator/frozen_inference_graph.pb'
        else:
            GRAPH_FILE = 'model/real_sdc/frozen_inference_graph.pb'

        self.confidence_cutoff = 0.5

        this_file_directory = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(this_file_directory, GRAPH_FILE)

        self.detection_graph = load_graph(model_path)
        # The input placeholder for the image.
        # `get_tensor_by_name` returns the Tensor with the associated name in the Graph.
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')

        # Each box represents a part of the image where a particular object was detected.
        self.boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')

        # Each score represent how level of confidence for each of the objects.
        self.scores = self.detection_graph.get_tensor_by_name('detection_scores:0')

        self.sess = tf.Session(graph=self.detection_graph)

        # The classification of the object (integer id).
        self.classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    def get_classification(self, image):
        """Determines the color of the traffic light in the image

        Args:
            image (cv::Mat): image containing the traffic light

        Returns:
            int: ID of traffic light color (specified in styx_msgs/TrafficLight)

        """
        #TODO implement light color prediction

        image_np = np.expand_dims(image, 0)
        #image_np = np.expand_dims(np.asarray(image, dtype=np.uint8), 0)

        with self.detection_graph.as_default():
            # Actual detection.
            (boxes, scores, classes) = self.sess.run([self.boxes,
                                                 self.scores,
                                                 self.classes],
                                                 feed_dict={self.image_tensor: image_np})

            # Remove unnecessary dimensions
            boxes = np.squeeze(boxes)
            scores = np.squeeze(scores)
            classes = np.squeeze(classes)

            # May be turned on for debug purposes
            if False:
                # The current box coordinates are normalized to a range between 0 and 1.
                # This converts the coordinates actual location on the image.

                # Filter boxes with a confidence score less than `confidence_cutoff`
                boxes, scores, classes = filter_boxes(self.confidence_cutoff, boxes, scores, classes)

                width, height = image.size
                box_coords = to_image_coords(boxes, height, width)

                # Each class with be represented by a differently colored box
                draw_boxes(image, box_coords, classes)
        #if True:
        #    classes = [1]
        #    scores = [1]

            #print("Classification: {0} with Score = {1}".format(label_map[classes[0]], scores[0]))

            #self.confidence_cutoff = 0.0
            if scores[0] > self.confidence_cutoff:
                if label_map[classes[0]] == 'red':
                    return TrafficLight.RED
                elif label_map[classes[0]] == 'yellow':
                    return TrafficLight.YELLOW
                elif label_map[classes[0]] == 'green':
                    return TrafficLight.GREEN

            return TrafficLight.UNKNOWN
