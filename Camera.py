from onvif import ONVIFCamera, ONVIFError


class Camera:
	def __init__(self, host, port, login, password):
		self.__camera = ONVIFCamera(host, port, login, password)
		self.__services = tuple(self.__camera.services_template.keys())
		self.__media = self.__camera.create_media_service()
		self.info()

	def get_available_services(self):
		return self.__services

	# def __init_services(self):
	# 	template = self.__camera.services_template
	# 	for serviceName in template.keys():
	# 		if template[serviceName]:
	# 			continue
	# 		getattr(self.__camera, f"create_{serviceName}_service")()
	# 		print("create service:", serviceName)

	def info(self):
		device = self.__camera.devicemgmt
		print("info:", device.GetDeviceInformation())

	def get_stream_uri(self):
		media = self.__media
		# capabilities = media.GetServiceCapabilities()
		profiles = media.GetProfiles()
		profile_token = profiles[0].token
		uri = media.GetStreamUri({
			"StreamSetup": {
				"Stream": "RTP-Unicast",
				"Transport": {"Protocol": "RTSP"}
			},
			"ProfileToken": profile_token
		})

		data = uri.Uri.split("/")
		protocol = data[0]
		host = data[2].split(":")[0]
		port = data[2].split(":")[1]
		path = "/".join(data[3:])
		return protocol, host, port, path

# media
# AddAudioDecoderConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434908>
# AddAudioEncoderConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814347B8>
# AddAudioOutputConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814348D0>
# AddAudioSourceConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814347F0>
# AddMetadataConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434898>
# AddPTZConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434828>
# AddVideoAnalyticsConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434860>
# AddVideoEncoderConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434748>
# AddVideoSourceConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434780>
# CreateOSD = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814376D8>
# CreateProfile = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814346A0>
# DeleteOSD = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437710>
# DeleteProfile = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434B38>
# GetAudioDecoderConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434EB8>
# GetAudioDecoderConfigurationOptions = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437400>
# GetAudioDecoderConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434CF8>
# GetAudioEncoderConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434DD8>
# GetAudioEncoderConfigurationOptions = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437358>
# GetAudioEncoderConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434C18>
# GetAudioOutputConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434E80>
# GetAudioOutputConfigurationOptions = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814373C8>
# GetAudioOutputConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434CC0>
# GetAudioOutputs = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434668>
# GetAudioSourceConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434DA0>
# GetAudioSourceConfigurationOptions = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437320>
# GetAudioSourceConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434BE0>
# GetAudioSources = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E811B8B70>
# GetCompatibleAudioDecoderConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814370B8>
# GetCompatibleAudioEncoderConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434F60>
# GetCompatibleAudioOutputConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437080>
# GetCompatibleAudioSourceConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434F98>
# GetCompatibleMetadataConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437048>
# GetCompatibleVideoAnalyticsConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434FD0>
# GetCompatibleVideoEncoderConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434EF0>
# GetCompatibleVideoSourceConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434F28>
# GetGuaranteedNumberOfVideoEncoderInstances = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437438>
# GetMetadataConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434E48>
# GetMetadataConfigurationOptions = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437390>
# GetMetadataConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434C88>
# GetOSD = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437630>
# GetOSDOptions = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437668>
# GetOSDs = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814375F8>
# GetProfile = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814346D8>
# GetProfiles = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434710>
# GetServiceCapabilities = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018EFFF6E828>
# GetSnapshotUri = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437550>
# GetStreamUri = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437470>
# GetVideoAnalyticsConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434E10>
# GetVideoAnalyticsConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434C50>
# GetVideoEncoderConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434D68>
# GetVideoEncoderConfigurationOptions = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814372E8>
# GetVideoEncoderConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434BA8>
# GetVideoSourceConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434D30>
# GetVideoSourceConfigurationOptions = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814372B0>
# GetVideoSourceConfigurations = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434B70>
# GetVideoSourceModes = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437588>
# GetVideoSources = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E813B4048>
# RemoveAudioDecoderConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434B00>
# RemoveAudioEncoderConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814349B0>
# RemoveAudioOutputConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434AC8>
# RemoveAudioSourceConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814349E8>
# RemoveMetadataConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434A90>
# RemovePTZConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434A20>
# RemoveVideoAnalyticsConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434A58>
# RemoveVideoEncoderConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434940>
# RemoveVideoSourceConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81434978>
# SetAudioDecoderConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437278>
# SetAudioEncoderConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437198>
# SetAudioOutputConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437240>
# SetAudioSourceConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437160>
# SetMetadataConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437208>
# SetOSD = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814376A0>
# SetSynchronizationPoint = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437518>
# SetVideoAnalyticsConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814371D0>
# SetVideoEncoderConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E81437128>
# SetVideoSourceConfiguration = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814370F0>
# SetVideoSourceMode = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814375C0>
# StartMulticastStreaming = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814374A8>
# StopMulticastStreaming = {OperationProxy} <zeep.proxy.OperationProxy object at 0x0000018E814374E0>
