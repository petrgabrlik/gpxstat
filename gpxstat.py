#!/usr/bin/env python3

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary


if __name__ == "__main__":

    import gpxpy
    import gpxpy.gpx
    import os
    import datetime
    import pytz
    import matplotlib.pyplot as plt
    import numpy as np
    from reportlab.pdfgen import canvas
    from geopy.distance import vincenty
    # import pandas as pd

    local_tz = pytz.timezone('Europe/Prague')

    gpxfiles = os.listdir('Cycle Tracks GPS')
    numOfRides = len(gpxfiles)
    print('Numger of GPX files: {:}'.format(numOfRides))

    startTimes = []
    durations = []
    distances = []
    weekdays = {'1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0}
    weekdaysl = []
    i = 0
    for filename in gpxfiles:
        # Open and parse
        gpx_file = open('Cycle Tracks GPS/' + filename, 'r')
        gpx = gpxpy.parse(gpx_file)
        i += 1
        print( '{:}%\t{:}'.format( int((i*100)/numOfRides), filename), end='\n')

        # Processing
        for track in gpx.tracks:
            for segment in track.segments:
                # Time
                startTime = utc_to_local(segment.points[0].time)
                endTime = utc_to_local(segment.points[-1].time)
                startTimes.append(startTime.hour)
                durations.append( int(((endTime - startTime).seconds)/60) )
                # print(segment.points[0].time.isoweekday())
                # weekdays[segment.points[0].time.isoweekday()] += 1
                weekdays[str(segment.points[0].time.isoweekday())] += 1
                weekdaysl.append(segment.points[0].time.isoweekday())

                # print(weekdays)

                # Distance
                lastPoint = None
                distance = 0
                for point in segment.points:
                    if lastPoint:
                        distance += vincenty([lastPoint.latitude,lastPoint.longitude], [point.latitude, point.longitude]).kilometers
                    lastPoint = point
                distances.append(distance)
        #break

    print()

    numberOfTracks = len(durations)
    durationMean = np.mean(durations)
    durationSum = sum(durations)/60
    distanceMean = np.mean(distances)
    distanceSum = sum(distances)

    #print('Start times')
    #print(startTimes)
    #print('Durations')
    #print(durations)
    print('Number of tracks: {:}'.format(numberOfTracks))
    print('Total distance: {:.0f} km'.format(distanceSum))
    print('Average distance: {:.1f} km'.format(distanceMean))
    print('Total duration: {:.0f} hours'.format(durationSum))
    print('Average duration: {:.0f} min'.format(durationMean))
    #print('Distances')
    #print(distances)

#    startTimesFreq = []
#    for time in range(24):
#        startTimesFreq.append(startTimes.count(time))
#        #print(startTimes.count(time))
#    print(startTimesFreq)

    fig1 = plt.figure(1)
    plt.subplot(221)
    # Plot histogram of rides by hours (during day)
    plt.hist(startTimes, 24, facecolor='green', alpha=0.75, range=(0, 24))
    plt.xlim([0, 24])
    plt.xlabel("Day hour")
    plt.ylabel("Ride count")
    plt.title('Rides by hours')
    plt.grid(True)
    #plt.show()

    #plt.figure(2)
    plt.subplot(222)
    # Plot histogram of durations of rides
    plt.hist(durations, 12, facecolor='green', alpha=0.75, range=(0, 120))
    #plt.hist(durations, 12, facecolor='green', alpha=0.75, range=(0, int(max(distances)+10))
    plt.xlim([0, 120])
    plt.xlabel("Duration [minutes]")
    plt.ylabel("Ride count")
    plt.title('Durations of rides')
    plt.grid(True)

    plt.subplot(223)
    plt.hist( distances, int(max(distances)+1), facecolor='green', alpha=0.75, range=(0, int(max(distances)+1)) )
    plt.xlim([0, int(max(distances)+1)])
    plt.xlabel("Distance [kilometers]")
    plt.ylabel("Ride count")
    plt.title('Distances of rides')
    plt.grid(True)

    plt.subplot(224)
    # plt.hist( distances, int(max(distances)+1), facecolor='green', alpha=0.75, range=(0, int(max(distances)+1)) )
    plt.hist(weekdaysl)
    # plt.bar(list(weekdays.keys()), list(weekdays.values()), color='g')
    # plt.xlim([0, int(max(distances)+1)])
    # plt.xlabel("Distance [kilometers]")
    # plt.ylabel("Ride count")
    # plt.title('Distances of rides')
    plt.grid(True)

    plt.show()

    c = canvas.Canvas("Report.pdf")
    c.drawString(100,750,"Report of bike rides")
    c.save()
