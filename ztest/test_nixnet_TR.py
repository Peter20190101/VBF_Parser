# Run with PYTHON 3.9 NOT 3.10 !!!
import nixnet
from nixnet import constants
from nixnet import types
count = 1
interface2 = 'can2'
# with nixnet.FrameInStreamSession('CAN1') as input_session:
    # input_session.intf.can_term = constants.CanTerm.ON
    # input_session.intf.can_term = nixnet._enums.CanTerm.ON
    # input_session.intf.baud_rate = 125000

    # frames = input_session.frames.read(count)
    # for frame in frames:
    #     print('Received frame:')
    #     print(frame)

with nixnet.FrameOutStreamSession(interface2) as output_session:
    output_session.intf.can_term = constants.CanTerm.ON
    output_session.intf.baud_rate = 500000
    payload_list = [2, 4, 8, 2]
    id = types.CanIdentifier(0)
    payload = bytearray(payload_list)
    frame = types.CanFrame(id, constants.FrameType.CAN_DATA, payload)

    frame.payload = payload
    output_session.frames.write([frame])
    output_session.close
