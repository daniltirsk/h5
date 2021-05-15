import time
import h5py 
import pytz
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timezone


def get_sites(pth):
    with h5py.File(pth, 'r') as f:
        sites = [site for site in f]
    return sites


def get_sats(pth, site, fhdf=None):
    f = h5py.File(pth, 'r') if not fhdf else fhdf
    if site in f:
        sats = [sat for sat in f[site]]
    if not fhdf:
        f.close()
    return sats


def get_data(pth, site, sat, field, fhdf=None):
    f = h5py.File(pth, 'r') if not fhdf else fhdf
    if site in f and sat in f[site]:
        times = f[site][sat][field][:]
    if not fhdf:
        f.close()
    return times


def get_series(pth, site, sat, field):
    ts = get_data(pth, site, sat, 'timestamp')
    data = get_data(pth, site, sat, field)
    return ts, data


def get_map(pth, time, field):
    result = []
    timestampss = {}
    timestamp = time.timestamp()
    t = datetime.utcfromtimestamp(timestamp).hour
    start = timestamp
    end = timestamp
    sites = get_sites(pth)
    f = h5py.File(pth, 'r+')
    map_indeces = []
    site_i = 0
    if 'maps' not in sites:
        f.create_group('maps')
    else:
        sites.remove('maps')
    #если карта уже была построена ранее
    if str(timestamp) in f['maps']:
        map_indeces = f['maps'][str(timestamp)]
        for i in range(0,len(map_indeces),3):
            site = sites[map_indeces[i]]
            lat = np.degrees(f[site].attrs['lat'])
            lon = np.degrees(f[site].attrs['lon'])
            sats = get_sats(pth, site, fhdf=f)
            sat = sats[map_indeces[i+1]]
            data_match = f[site][sat][field][map_indeces[i+2]]
            result.append((data_match, lon, lat))
        return np.array(result)
    else:
        #иначе строим как обычно
        for site in sites:
            lat = np.degrees(f[site].attrs['lat'])
            lon = np.degrees(f[site].attrs['lon'])
            sats = get_sats(pth, site, fhdf=f)
            sat_i = -1
            for sat in sats:
                sat_i += 1
                timestamps = get_data(pth, site, sat, 'timestamp', fhdf=f)
                
                if timestamps[0]>timestamp:
                    continue
                if timestamps[-1]<timestamp:
                    continue
                if timestamp not in timestamps:
                    continue

                            
                data = get_data(pth, site, sat, field, fhdf=f)
                match = timestamps.searchsorted(timestamp)
                data_match = data[match]
                map_indeces += [site_i,sat_i,match]
                result.append((data_match, lon, lat))

            site_i += 1
    if not result:
        return None
    else:
        #сохранаяем индексы в файл
        f['maps'].create_dataset(str(timestamp),data=map_indeces)
        return np.array(result)
        


if __name__ == '__main__':
    plot_map = True
    pth = '2020-05-20.h5'
    if not plot_map:
        timestamps, data = get_series(pth, 'arsk', 'G03', 'dtec_10_20')
        times = [datetime.fromtimestamp(t, pytz.utc) for t in timestamps]
        plt.scatter(times, data)
        plt.xlim(times[0], times[-1])
        plt.show()
    else:
        epoch = datetime(2020, 5, 20, 12, 30, 0, tzinfo=timezone.utc)
        before = time.time()
        data = get_map(pth, epoch, 'dtec_10_20')
        print(f'It took {time.time() - before} sec. to retrieve a map')
        val = data[:, 0]
        x = data[:, 1]
        y = data[:, 2]
        plt.scatter(x, y, c=val)
        plt.xlim(-180, 180)
        plt.ylim(-90, 90)
        plt.show()
    


