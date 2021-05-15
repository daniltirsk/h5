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


def get_data(pth, site, sat, h, field, fhdf=None):
    f = h5py.File(pth, 'r') if not fhdf else fhdf
    if site in f and sat in f[site]:
        times = f[site][sat][h][field][:]
    if not fhdf:
        f.close()
    return times


def get_series(pth, site, sat, field):
    ts = get_data(pth, site, sat, 'timestamp')
    data = get_data(pth, site, sat, field)
    return ts, data


def get_map(pth, time, field):
    result = []
    timestamp = time.timestamp()
    h = str(datetime.utcfromtimestamp(timestamp).hour)
    start = timestamp
    end = timestamp
    sites = get_sites(pth)
    f = h5py.File(pth, 'r')
    for site in sites:
        lat = np.degrees(f[site].attrs['lat'])
        lon = np.degrees(f[site].attrs['lon'])
        sats = get_sats(pth, site, fhdf=f)
        for sat in sats:
            data = get_data(pth, site, sat, h, field, fhdf=f)
            #если дата для часа пустая, то пропуск
            if len(data) == 0:
               continue
            
            timestamps = get_data(pth, site, sat, h, 'timestamp', fhdf=f)


            
            match = np.where((timestamps >= start) & (timestamps <= end))
            data_match = data[match]
            for d in data_match:
                result.append((d, lon, lat))
    if not result:
        return None
    else:
        return np.array(result)
        


if __name__ == '__main__':
    plot_map = True
    pth = 'n1.h5'
    if not plot_map:
        timestamps, data = get_series(pth, 'arsk', 'G03', 'dtec_20_60')
        times = [datetime.fromtimestamp(t, pytz.utc) for t in timestamps]
        plt.scatter(times, data)
        plt.xlim(times[0], times[-1])
        plt.show()
    else:
        epoch = datetime(2020, 5, 20, 12, 30, 0, tzinfo=timezone.utc)
        before = time.time()
        data = get_map(pth, epoch, 'dtec_20_60')
        print(f'It took {time.time() - before} sec. to retrieve a map')
        val = data[:, 0]
        x = data[:, 1]
        y = data[:, 2]
        plt.scatter(x, y, c=val)
        plt.xlim(-180, 180)
        plt.ylim(-90, 90)
        plt.show()
        
'''
#кусок кода использованный для перезаписи файла 
with h5py.File('n1.h5', 'w') as f2:
    with h5py.File(pth, 'r+') as f:
        sites = get_sites(pth)
        for site in sites:
            print(site)
            f2.create_group(site)
            sats = get_sats(pth, site, fhdf=f)
            for sat in sats:
                f2[site].create_group(sat)
                for k in data.keys():
                    data[k] = 0
                    
                data2 = {}
            
                for d in list(f[site][sat].keys()):
                    data2[d] = get_data(pth, site, sat, d, fhdf=f)
                      
                for i in data.keys():
                    f2[site][sat].create_group(i)
                for i in range(0,len(data2['timestamp'])):
                    t = datetime.utcfromtimestamp(data2['timestamp'][i]).hour
                    data[str(t)]+=1  

                data_values = list(data.values())
                
                for t in data.keys():
                    for k in data2.keys():
                        if int(t) != 0:
                            f2[site][sat][t].create_dataset(k, data=data2[k][sum(data_values[0:int(t)]):sum(data_values[0:int(t)+1])])
                        else:
                            f2[site][sat][t].create_dataset(k, data=data2[k][0:data[t]])
             
with h5py.File('n1.h5', 'r+') as f2:
    with h5py.File(pth, 'r+') as f:
        sites = get_sites(pth)
        for site in sites:
            lat = f[site].attrs['lat']
            lon = f[site].attrs['lon']

            f2[site].attrs['lat'] = lat
            f2[site].attrs['lon'] = lon
'''




