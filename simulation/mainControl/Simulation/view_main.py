import rospy  # ros在python语言中的头文件
from std_msgs.msg import String  # 消息头文件

message = ''

def callback(data):
    global message
    message = data.data

if __name__ == '__main__':
    rospy.init_node('view_listener', annoymous= True)
    rospy.Subscriber('view_data', String, callback)
    while message == '':
        continue
    print(message)
    view_message = eval(message)
    print(view_message)