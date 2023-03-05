"""
This is by no means a full/proper ISOTP implementation. It aims to work with just the BROKEN Ford implementation.


This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""
import six
import sys
from time import sleep
from io import BytesIO
# import can
import nixnet
from nixnet import constants
from nixnet import types

class SimpleISOTP:
	def __init__(self, can_interface, can_tx, can_rx):
		self.state = 0
		self.can_id = can_tx
		# try:
		# 	# self.bus = can.interface.Bus(bustype='socketcan', channel=can_interface, bitrate=500000, receive_own_messages=False)
		# 	self.bus = can.interface.Bus(bustype='nixnet', channel=can_interface, bitrate=500000, receive_own_messages=False)
		# 	# self.output_session = nixnet.FrameOutStreamSession('can1')
			
		# 	# id = types.CanIdentifier(0)
		# 	# # payload = bytearray(msg)
		# 	# payload_list = [2, 4, 8, 2]
		# 	# # payload = bytearray(payload_list)
		# 	# payload = msg
		# 	# frame = types.CanFrame(id, constants.FrameType.CAN_DATA, payload)
		# 	# frame.payload = payload
		# 	# self.output_session.frames.write([frame])
		# 	# self.output_session.close

		# except can.CanError as e:
		# 	print("[!] Unable to open {}".format(can_interface))
		# 	sys.exit(-1)

		# can_filters = [{"can_id": can_rx, "can_mask": 0xfff, "extended": False}]
		# self.bus.set_filters(can_filters)

	def putoncan(self, msg):
		sleep(0.002)
		with nixnet.FrameOutStreamSession('can1') as output_session:
			# with nixnet.FrameInStreamSession('can2') as input_session:
				output_session.intf.can_term = constants.CanTerm.ON
				output_session.intf.baud_rate = 500000

				# input_session.intf.can_term = constants.CanTerm.ON
				# input_session.intf.baud_rate = 500000

				# input_session.start()
				id = types.CanIdentifier(self.can_id)
				payload = msg
				frame = types.CanFrame(id, constants.FrameType.CAN_DATA, payload)
				frame.payload = payload
				output_session.frames.write([frame])

				# count = 1
				# frames = input_session.frames.read(count)
				# for frame in frames:
				# 	print('Received frame with ID: {} payload: {}'.format(frame.identifier,list(six.iterbytes(frame.payload))))

	def send(self, payload):
		size = len(payload)

		if size < 8:
			self.state = 0
			data = bytearray([len(payload)]) + payload + bytearray([0x00] * (7-size))
			self.putoncan(data)
		else:
			data = bytearray().fromhex('1{:03x}'.format(size)) + payload[:6]
			self.putoncan(data)
			# while True:
			# 	fc = self.bus.recv()
			# 	if fc.data[0] & 0xf0 == 0x30:
			# 		break

			self.state = 1
			ds = BytesIO(payload[6:])

			while True:
				part = ds.read(7)
				if not part:
					self.state = 0
					break

				data = bytearray([0x20+self.state]) + part + bytearray([0x00] * (7-len(part)))
				self.putoncan(data)
				if self.state < 0x0f:
					self.state += 1
				else:
					self.state = 0

	def recv1(self):
		with nixnet.FrameInStreamSession('can2') as input_session:
			input_session.intf.can_term = constants.CanTerm.OFF
			input_session.intf.baud_rate = 500000
			input_session.start()
			count = 1
			frames = input_session.frames.read(count)
			for frame in frames:
				print('Received frame with ID: {} payload: {}'.format(frame.identifier,list(six.iterbytes(frame.payload))))

	def recv(self):
		while True:
			# data = self.bus.recv().data
			with nixnet.FrameInStreamSession('can2') as input_session:
				input_session.intf.can_term = constants.CanTerm.ON
				# input_session.intf.can_term = nixnet._enums.CanTerm.ON
				input_session.intf.baud_rate = 500000
				count = 1
				data = input_session.frames.read(count)
				# for frame in frames:
				# 	print('Received frame:')
				# 	print(frame)
			# print("DEBUG: {}".format(data))
			if not data:

				return None

			# fd0 = frames[0].identifier
			# fd1 = list(six.iterbytes(frames[0].payload))
			for frame in data:
				print('Received frame with ID: {} payload: {}'.format(frame.identifier,list(six.iterbytes(frame.payload))))

			if self.state == 0 and (data[0] & 0xf0 == 0x10):
				self.state = 1
				size = (data[0] & 0x0f) * 0x100 + data[1]
				buf = BytesIO()
				received = 6
				buf.write(data[2:])

				data = bytearray([0x30]) + bytearray([0x00] * 7)
				# msg = can.Message(arbitration_id=self.can_id, data=data, is_extended_id=False)				
				self.putoncan(data)

			if self.state > 0 and (data[0] & 0xf0 == 0x20):
				self.state = 2

				if(received + 7 > size):
					buf.write(data[1:1+size-received])
				else:
					buf.write(data[1:])

				received += 7
				if received >= size:
					self.state = 0
					buf.seek(0)
					return buf.read()


			if self.state == 0 and (data[0] & 0xf0 != 0x30):
				size = data[0]
				return data[1:size+1]
		
can_interface = "can1"
ecuid = 400
aa = SimpleISOTP(can_interface, ecuid, ecuid+0x08)
aa.send(bytearray([0x13, 0x01]))
# sleep(1)
# aa.recv1()
# aa.send(bytearray([0x11, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01]))

# can_interface = "can2"
# ecuid = 400
# bb = SimpleISOTP(can_interface, ecuid, ecuid+0x08)
# rx = aa.recv()
# print(rx)