# -*- coding:utf-8 -*-
import cv2
import math
import numpy as np
from utils.anchor_generator import generate_anchors
from utils.anchor_decode import decode_bbox
from utils.nms import single_class_non_max_suppression
from load_model.pytorch_loader import load_pytorch_model, pytorch_inference

model = load_pytorch_model('models/model360.pth');

# anchor configuration
#feature_map_sizes = [[33, 33], [17, 17], [9, 9], [5, 5], [3, 3]]
feature_map_sizes = [[45, 45], [23, 23], [12, 12], [6, 6], [4, 4]]
anchor_sizes = [[0.04, 0.056], [0.08, 0.11], [0.16, 0.22], [0.32, 0.45], [0.64, 0.72]]
anchor_ratios = [[1, 0.62, 0.42]] * 5

# generate anchors
anchors = generate_anchors(feature_map_sizes, anchor_sizes, anchor_ratios)

# for inference , the batch size is 1, the model output shape is [1, N, 4],
# so we expand dim for anchors to [1, anchor_num, 4]
anchors_exp = np.expand_dims(anchors, axis=0)

#ponemos etiqutas, el 0 es mascarilla y el 1 no mascarilla
id2class = {0: 'Mascarilla', 1: 'No_Mascarilla'}


def reconocimientoFacial(image,
              max_distancia_centro,
              conf_thresh=0.5,
              iou_thresh=0.5,
              target_shape=(360, 360),
              draw_result=True,
              ):
    '''
    Main function of detection inference
    :param image: 3D numpy array of image
    :param conf_thresh: the min threshold of classification probabity.
    :param iou_thresh: the IOU threshold of NMS
    :param target_shape: the model input size.
    :param draw_result: whether to daw bounding box to the image.
    '''
    #convertimos la imagen que llega
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    height, width, _ = image.shape
    image_resized = cv2.resize(image, target_shape)
    image_np = image_resized / 255.0
    image_exp = np.expand_dims(image_np, axis=0)

    image_transposed = image_exp.transpose((0, 3, 1, 2))

    y_bboxes_output, y_cls_output = pytorch_inference(model, image_transposed)
    # remove the batch dimension, for batch is always 1 for inference.
    y_bboxes = decode_bbox(anchors_exp, y_bboxes_output)[0]
    y_cls = y_cls_output[0]
    # To speed up, do single class NMS, not multiple classes NMS.
    bbox_max_scores = np.max(y_cls, axis=1)
    bbox_max_score_classes = np.argmax(y_cls, axis=1)

    # keep_idx is the alive bounding box after nms.
    keep_idxs = single_class_non_max_suppression(y_bboxes,
                                                 bbox_max_scores,
                                                 conf_thresh=conf_thresh,
                                                 iou_thresh=iou_thresh,
                                                 )
    #variables para calcular la cara del centro
    center_face_X = 0
    center_face_Y = 0
    distancia_al_centro = math.inf
    cara_detectada = False
    #inicilizamos a no mascarilla, que es true
    #mascarilla es false, al final invertimos el resultado
    class_id = True
    
    for idx in keep_idxs:
        cara_detectada = True
        conf = float(bbox_max_scores[idx])
        class_id = bbox_max_score_classes[idx]
        bbox = y_bboxes[idx]
        #coordenadas minimas y maximas de la cara
        xmin = max(0, int(bbox[0] * width))
        ymin = max(0, int(bbox[1] * height))
        xmax = min(int(bbox[2] * width), width)
        ymax = min(int(bbox[3] * height), height)
        
        #calculamos el centro de la ara concreta
        centerX = round((xmax + xmin) / 2)
        centerY = round((ymax + ymin) / 2)
            
        distancia = math.sqrt(((centerX-(width/2))**2)+((centerY-(height/2))**2))
            
        #guardamos para quedarnos con la más cercana al centro
        if distancia < distancia_al_centro:
            distancia_al_centro = distancia
            center_face_X = centerX
            center_face_Y = centerY
            
        #dibujamos recuado en la cara detectada
        if draw_result:
            if class_id == 0:
                color = (0, 255, 0)
            else:
                color = (255, 0, 0)
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
            cv2.putText(image, "%s: %.2f" % (id2class[class_id], conf), (xmin + 2, ymin - 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color)
    
    #inicialiamos la variable que detecta si la cara esta en el circulo a false
    locked = False
    
    #dibujamos el circulo y el centro de la cara con distancia mas cercana al centro
    if distancia_al_centro != math.inf and draw_result:
        if distancia_al_centro < max_distancia_centro:
            locked = True
            color = (0, 255, 0)
        else:
            locked = False
            color = (255, 0, 0)

        cv2.rectangle(image,(center_face_X-10, center_face_Y), (center_face_X+10, center_face_Y), color, 2)
        cv2.rectangle(image,(center_face_X, center_face_Y-10), (center_face_X, center_face_Y+10), color, 2)
        cv2.circle(image, (int(width/2), int(height/2)), int(max_distancia_centro) , color, 2)   

    center_face_X = center_face_X-(width/2)
    center_face_Y = center_face_Y-(height/2)
    
    #inverimos class id para que false sea no mascarilla
    return [cara_detectada, image, center_face_X, center_face_Y, locked, not class_id]
