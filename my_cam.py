import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
import cv2
import numpy as np

class publish_bytes_data(Node):
    def __init__(self,name):
        super().__init__(name)
        self.publisher_ = self.create_publisher(CompressedImage,'byte_data_topic',10)
        self.timer = self.create_timer(1/30, self.timer_callback)
        self.cv_bridge = CvBridge()

        # 打开摄像头（通常使用默认摄像头，索引为0）
        self.cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
        #cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)      # 解决问题的关键！！！
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480 )
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        if not self.cap.isOpened():
            print("无法打开摄像头")
            exit()

    def timer_callback(self):
        # 从摄像头读取一帧图像
        ret, frame = self.cap.read()
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50] # 压缩率10 占用带宽500kb以内，压缩率90 占用带宽最高2-3M
        _,encoding = cv2.imencode('.jpg', frame, encode_param) # 开始压缩 上面使用了JPGE压缩算法
        jpg_data = encoding.tobytes() # 转换成字节码
        decoding = cv2.imdecode(np.frombuffer(jpg_data,np.uint8),cv2.IMREAD_COLOR) # 解压生成图像
        self.publisher_.publish(self.cv_bridge.cv2_to_compressed_imgmsg(decoding,dst_format='jpeg')) # 图像传输，走ros2的sensor_msgs.msg/CompressedImage,使用cv2_to_compressed_imgmsg函数

        print("压缩完毕!! start image transport")


        #jpg_data = encoding.tobytes()
        #print("压缩完成，压缩结果：")
        #print(_)
        #print("开始发")

def main(args = None):
    rclpy.init(args=args)
    node = publish_bytes_data("cam_publisher")
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
