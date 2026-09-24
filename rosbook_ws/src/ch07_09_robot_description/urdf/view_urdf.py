import pybullet as p
import pybullet_data
import time

# PyBullet GUI 실행
physicsClient = p.connect(p.GUI)

# 카메라 위치 설정
p.resetDebugVisualizerCamera(
    cameraDistance=2.5,
    cameraYaw=45,
    cameraPitch=-30,
    cameraTargetPosition=[0, 0, 0]
)

# 기본 데이터 경로 설정
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# 중력 설정
p.setGravity(0, 0, -9.81)

# 바닥 생성
planeId = p.loadURDF("plane.urdf")

# 작성한 로봇 URDF 로드
robotId = p.loadURDF(
    "temp.urdf",
    [0, 0, 0.5]
)

# Joint 정보 출력
num_joints = p.getNumJoints(robotId)

print(f"Joint 개수: {num_joints}")

for i in range(num_joints):

    joint_info = p.getJointInfo(robotId, i)

    print(
        f"Joint [{i}] : "
        f"{joint_info[1].decode('utf-8')}"
    )

print("PyBullet URDF Viewer 실행")

try:

    while True:

        p.stepSimulation()
        time.sleep(1.0 / 240.0)

except KeyboardInterrupt:

    p.disconnect()