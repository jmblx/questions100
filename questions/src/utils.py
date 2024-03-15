def get_sample_and_delete(sheet_name, data_frame_dict):
    sample_obj = data_frame_dict[sheet_name].sample()
    data_frame_dict[sheet_name].drop(sample_obj.index, inplace=True)
    return sample_obj
