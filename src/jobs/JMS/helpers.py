from resource_managers.objects import *

def parse_settings_list(settings_list):
    settings = []
    for s in settings_list:
        s = Setting(s["Key"], s["Value"])
        settings.append(s)
    return settings

def parse_settings_sections_dict(settings_sections_dict):
    settings_sections = []
    for section in settings_sections_dict:
        ss = SettingsSection(section["SectionHeader"], [])
        for setting in section["Settings"]:
            s = Setting(setting["Key"], setting["Value"])
            ss.Settings.append(s)
        settings_sections.append(ss)
    return settings_sections


def parse_node_dict(node_dict):
    name = node_dict["Name"]
    state = node_dict["State"]
    num_cores = node_dict["NumCores"]
    other = node_dict["Other"]
    return Node(name=name, state=state, num_cores=num_cores, busy_cores=None, free_cores=None, other=other)


def parse_admin_dict(admin_dict):
    admin = Administrator(admin_dict["AdministratorName"], 
        parse_settings_sections_dict(admin_dict["SettingsSections"]))
    return admin


def parse_queue_dict(queue_dict):
    queue = Queue(queue_dict["QueueName"], 
        parse_settings_sections_dict(queue_dict["SettingsSections"]))
    return queue