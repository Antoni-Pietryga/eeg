from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import mne
import os
import json
import base64
import matplotlib.pyplot as plt


sample_data_folder = mne.datasets.sample.data_path()
sample_data_raw_file = os.path.join(sample_data_folder, 'MEG', 'sample', 'sample_audvis_raw.fif')

    
def get_channels():
    raw = mne.io.read_raw_fif(sample_data_raw_file, preload=True, verbose=False)
    eeg_ch = [raw.ch_names[i] for i in mne.pick_types(raw.info, eeg=True)]
    emg_ch = [raw.ch_names[i] for i in mne.pick_types(raw.info, emg=True)]
    sti_ch = [raw.ch_names[i] for i in mne.pick_types(raw.info, stim=True)]
    eog_ch = [raw.ch_names[i] for i in mne.pick_types(raw.info, eog=True)]
    meg_ch = [raw.ch_names[i] for i in mne.pick_types(raw.info, meg=True)]
    ecg_ch = [raw.ch_names[i] for i in mne.pick_types(raw.info, ecg=True)]
    ref_meg_ch = [raw.ch_names[i] for i in mne.pick_types(raw.info, ref_meg=True)]
    misc_ch = [raw.ch_names[i] for i in mne.pick_types(raw.info, misc=True)]
    
    return {"eeg": eeg_ch, "meg": meg_ch, } # "sti": sti_ch, "eog": eog_ch, "meg": meg_ch, "ecg":ecg_ch, "ref_meg": ref_meg_ch, "misc": misc_ch

def chart_meg(channels):
    raw = mne.io.read_raw_fif(sample_data_raw_file, preload=True, verbose=False)
    
    raw = raw.copy().pick_channels(channels + [raw.ch_names[i] for i in mne.pick_types(raw.info, stim=True)])
    
    raw_highpass = raw.copy().filter(l_freq=0.1, h_freq=None)
    raw_filtered = raw_highpass.copy().filter(None, 30., fir_design='firwin')
    event_id = {'Standard': 2, 'Target': 4}
    events = mne.find_events(raw_filtered, stim_channel='STI 014')
    baseline = (-0.1, 0)
    epochs = mne.Epochs(raw, events=events, event_id=event_id, tmin=-0.1, tmax=0.5, baseline=baseline, reject=None)
    fig = epochs.plot(block=True, show=False)
    fig.savefig("meg1.png")
    
    
    epochs = mne.Epochs(raw_filtered, events, tmin=-0.1, tmax=0.5)
    fig = epochs.plot(n_epochs=20, show=False)
    fig.savefig("meg2.png")
    
    with open("meg1.png", "rb") as image_file:
        meg1 = base64.b64encode(image_file.read()).decode('utf-8')
        
    with open("meg2.png", "rb") as image_file:
        meg2 = base64.b64encode(image_file.read()).decode('utf-8')
    
    return meg1, meg2


def evoked(channels):
    raw = mne.io.read_raw_fif(sample_data_raw_file, preload=True, verbose=False)
    raw = raw.copy().pick_channels(channels + [raw.ch_names[i] for i in mne.pick_types(raw.info, stim=True)])
    
    events = mne.find_events(raw, stim_channel='STI 014')
    event_id = {'Standard': 2, 'Target': 4}
    baseline = (-0.1, 0)
    epochs = mne.Epochs(raw, events=events, event_id=event_id, tmin=-0.1,
                        tmax=0.5, baseline=baseline, reject=None)
    
    picks = mne.pick_types(epochs.info, eeg=True)

    evoked_standard = epochs['Standard'].average(picks=picks)
    evoked_target = epochs['Target'].average(picks=picks)

    fig = evoked_target.plot(spatial_colors=True, show=False)
    fig.savefig("evoked_target.png")
    
    fig = evoked_standard.plot(spatial_colors=True, show=False)
    fig.savefig("evoked_standard.png")

def create_sensors_chart(channels):
    raw = mne.io.read_raw_fif(sample_data_raw_file, preload=True, verbose=False)
    ch_type = None
    
    if "Wszystkie meg" in channels:
        raw = raw.pick_channels([raw.ch_names[i] for i in mne.pick_types(raw.info, meg=True)])
        ch_type = "MEG"
    elif "Wszystkie eeg" in channels:
        raw = raw.pick_channels([raw.ch_names[i] for i in mne.pick_types(raw.info, eeg=True)])
        ch_type = "EEG"
    else:
        eeg_list = []
        meg_list = []
        for ch_name in channels:
            if ch_name.find("EEG") != -1:
                eeg_list.append(ch_name)
            elif ch_name.find("MEG") != -1:
                meg_list.append(ch_name)
        if len(meg_list) > len(eeg_list):
            channels = meg_list
            ch_type = "MEG"
        else:
            channels = eeg_list
            ch_type = "EEG"
        raw = raw.pick_channels(channels)
    
 
    fig_2d = raw.plot_sensors(show=False, show_names=True)
    fig_3d = raw.plot_sensors(kind='3d', show=False)
    os.remove("umiejscowienie_elektrod_2d.png")
    os.remove("umiejscowienie_elektrod_3d.png")
    fig_2d.savefig("umiejscowienie_elektrod_2d.png")
    fig_3d.savefig("umiejscowienie_elektrod_3d.png")
    
    
    with open("umiejscowienie_elektrod_2d.png", "rb") as image_file:
        image_data_2d = base64.b64encode(image_file.read()).decode('utf-8')

    with open("umiejscowienie_elektrod_3d.png", "rb") as image_file:
        image_data_3d = base64.b64encode(image_file.read()).decode('utf-8')

    
    if ch_type == "EEG":
        eeg_chanels = [raw.ch_names.index(i) for i in channels]
        fig = raw.plot(duration=10, order=eeg_chanels, n_channels=len(eeg_chanels), show=False)
        fig.savefig("niefiltrowane_eeg.png")
        evoked(channels)
        
        with open("niefiltrowane_eeg.png", "rb") as image_file:
            image_data_eeg_notf = base64.b64encode(image_file.read()).decode('utf-8')
        
        with open("evoked_target.png", "rb") as image_file:
            evoked_target = base64.b64encode(image_file.read()).decode('utf-8')

        with open("evoked_standard.png", "rb") as image_file:
            evoked_standard = base64.b64encode(image_file.read()).decode('utf-8')

        
        return {"status":"ok", "img_data_2d":image_data_2d,  "img_data_3d":image_data_3d, "chart_data": image_data_eeg_notf, "ch_type": "EEG", "evoked_target":evoked_target, "evoked_standard": evoked_standard}
    
    elif ch_type == "MEG":      
        emg1, emg2 = chart_meg(channels)
        return {"status":"ok", "img_data_2d":image_data_2d,  "img_data_3d":image_data_3d, "chart_data_1": emg1, "chart_data_2":emg2, "ch_type": "MEG"}


def apply_filter(high, low, channels):
    raw = mne.io.read_raw_fif(sample_data_raw_file, preload=True, verbose=False)
    if high == "0":
        high = None
    else:   
        high = float(high)
    if low == "0": 
        low = None 
    else: 
        low = float(low)
        
    
    if "Wszystkie meg" in channels:
        raw = raw.pick_channels([raw.ch_names[i] for i in mne.pick_types(raw.info, meg=True)])
        ch_type = "MEG"
    elif "Wszystkie eeg" in channels:
        raw = raw.pick_channels([raw.ch_names[i] for i in mne.pick_types(raw.info, eeg=True)])
        ch_type = "EEG"
    else:
        eeg_list = []
        meg_list = []
        for ch_name in channels:
            if ch_name.find("EEG") != -1:
                eeg_list.append(ch_name)
            elif ch_name.find("MEG") != -1:
                meg_list.append(ch_name)
        if len(meg_list) > len(eeg_list):
            channels = meg_list
            ch_type = "MEG"
        else:
            channels = eeg_list
            ch_type = "EEG"
        raw = raw.pick_channels(channels)    
        
        
    raw = raw.filter(l_freq=low, h_freq=high)
    eeg_chanels = [raw.ch_names.index(i) for i in channels]
    fig = raw.plot(duration=10, order=eeg_chanels, n_channels=len(eeg_chanels), show=False)
    fig.savefig("filtrowane_eeg.png")
    with open("filtrowane_eeg.png", "rb") as image_file:
        image_data_eeg_f = base64.b64encode(image_file.read()).decode('utf-8')
    return image_data_eeg_f    



    
def index(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('ascii'))
        if data["action"] == "send_channels":
            
            print(json.loads(request.body.decode('ascii')))
            data = create_sensors_chart(data["channels"])
             
            return JsonResponse(data)
        elif data["action"] == "send_filter":
            with open("evoked_target.png", "rb") as image_file:
                evoked_target = base64.b64encode(image_file.read()).decode('utf-8')

            with open("evoked_standard.png", "rb") as image_file:
                evoked_standard = base64.b64encode(image_file.read()).decode('utf-8')
        
            return JsonResponse({"data":apply_filter(data["high_pass"], data["low_pass"], data["channels"]), "evoked_target":evoked_target, "evoked_standard": evoked_standard})
        
    context = {"channels": get_channels()}
    return render(request, 'main.html', context)


