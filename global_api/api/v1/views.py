import datetime as dt
import json
import time
import urllib
from collections import defaultdict

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

SHIFT_API_URL = 'https://gitlab.com/-/snippets/2094509/raw/master/sample_json_1.json'
MACHINE_API_URL = 'https://gitlab.com/-/snippets/2094509/raw/master/sample_json_2.json'
BELT_API_URL = 'https://gitlab.com/-/snippets/2094509/raw/master/sample_json_3.json'

'''creating a class to calculate the shift count''' 

class ShiftCountApi(APIView):
    def get(self, request):
#checking the user queries in a try block
        try:
            start_time = dt.datetime.strptime(request.query_params.get("start_time"), "%Y-%m-%dT%H:%M:%SZ")
            end_time = dt.datetime.strptime(request.query_params.get("end_time"), "%Y-%m-%dT%H:%M:%SZ")
        except TypeError:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        result = urllib.request.urlopen(SHIFT_API_URL)
        data = json.loads(result.read())

#lambda function to filter out values in the given time intervals

        filter_date_range = lambda x: True if start_time <= dt.datetime.strptime(
            x['time'], "%Y-%m-%d %H:%M:%S") < end_time else False
        filtered_data = filter(filter_date_range, data)
        shifts = {"shiftA":
            {
                "start": dt.time(6),
                "end": dt.time(14)
            },
            "shiftB":
                {
                    "start": dt.time(14),
                    "end": dt.time(20)
                },
            "shiftC":
                {
                    "start": dt.time(20),
                    "end": dt.time(6)
                },
        }
        shift_count = {
            "shiftA": {"production_A_count": 0, "production_B_count": 0},
            "shiftB": {"production_A_count": 0, "production_B_count": 0},
            "shiftC": {"production_A_count": 0, "production_B_count": 0},
        }
        for shift in filtered_data:
            time1 = dt.datetime.strptime(shift['time'], "%Y-%m-%d %H:%M:%S").time()
            if shifts['shiftA']['start'] < time1 < shifts['shiftA']['end']:
                shift_count['shiftA']['production_A_count'] = shift_count['shiftA']['production_A_count'] + 1 if shift[
                    'production_A'] else shift_count['shiftA']['production_A_count']
                shift_count['shiftA']['production_B_count'] = shift_count['shiftA']['production_B_count'] + 1 if shift[
                    'production_B'] else shift_count['shiftA']['production_B_count']

            elif shifts['shiftB']['start'] < time1 < shifts['shiftB']['end']:
                shift_count['shiftB']['production_A_count'] = shift_count['shiftB']['production_A_count'] + 1 if shift[
                    'production_A'] else shift_count['shiftB']['production_A_count']
                shift_count['shiftB']['production_B_count'] = shift_count['shiftB']['production_B_count'] + 1 if shift[
                    'production_B'] else shift_count['shiftB']['production_B_count']
            else:
                shift_count['shiftC']['production_A_count'] = shift_count['shiftC']['production_A_count'] + 1 if shift[
                    'production_A'] else shift_count['shiftC']['production_A_count']
                shift_count['shiftC']['production_B_count'] = shift_count['shiftC']['production_B_count'] + 1 if shift[
                    'production_B'] else shift_count['shiftC']['production_B_count']

        return Response(shift_count)

'''class to find out the total run time, downtime and machine utilization
in a given time inetrval'''
class MachineUtilization(APIView):
    def get(self, request):
        try:
            
            start_time = dt.datetime.strptime(request.query_params.get("start_time"), "%Y-%m-%dT%H:%M:%SZ")
            end_time = dt.datetime.strptime(request.query_params.get("end_time"), "%Y-%m-%dT%H:%M:%SZ")
        except TypeError:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        result = urllib.request.urlopen(MACHINE_API_URL)
        data = json.loads(result.read())

        filter_daterange = lambda x: True if start_time < dt.datetime.strptime(
            x['time'], "%Y-%m-%d %H:%M:%S") < end_time else False
        filtered_data = filter(filter_daterange, data)
        max_runtime = 1021
        machine_data = {
            'runtime': 0,
            'downtime': 0,
            'utilisation': 0
        }
        for data in filtered_data:
            machine_data['runtime'] += data['runtime']
            if data['runtime'] > max_runtime:
                machine_data['downtime'] += (data['runtime'] - max_runtime)

        machine_data['utilisation'] = (machine_data['runtime']) / (
                machine_data['runtime'] + machine_data['downtime']) * 100
        machine_data['runtime'] = time.strftime("%Hh:%Mm:%Ss", time.gmtime(machine_data['runtime']))
        machine_data['downtime'] = time.strftime("%Hh:%Mm:%Ss", time.gmtime(machine_data['downtime']))

        return Response(machine_data)

''' a class to find out average of belt1 and belt2 in the given time interval'''

class BeltAverage(APIView):
    def get(self, request):
        try:
            start_time = dt.datetime.strptime(request.query_params.get("start_time"), "%Y-%m-%dT%H:%M:%SZ")
            end_time = dt.datetime.strptime(request.query_params.get("end_time"), "%Y-%m-%dT%H:%M:%SZ")
        except TypeError:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        result = urllib.request.urlopen(BELT_API_URL)
        data = json.loads(result.read())

        filter_daterange = lambda x: True if start_time <= dt.datetime.strptime(
            x['time'], "%Y-%m-%d %H:%M:%S") <= end_time else False
        filtered_data = filter(filter_daterange, data)
        total_data = defaultdict(dict)
        for data in filtered_data:
            if data['state'] == True:
                data['belt1'] = 0
            else:
                data['belt2'] = 0

            if data['id'][-1] not in total_data.keys():
                total_data[data['id'][-1]]['avg_belt1'] = data['belt1']
                total_data[data['id'][-1]]['avg_belt2'] = data['belt2']
                total_data[data['id'][-1]]['count'] = 1
                total_data[data['id'][-1]]['id'] = data['id'][-1]
            else:

                total_data[data['id'][-1]]['avg_belt1'] += data['belt1']
                total_data[data['id'][-1]]['avg_belt2'] += data['belt2']
                total_data[data['id'][-1]]['count'] += 1
                total_data[data['id'][-1]]['id'] = data['id'][-1]

#creating a dictionary with the output values
        output_data = [
            {
                "id": v['id'],
                "avg_belt1": (v['avg_belt1'] / v['count']),
                "avg_belt2": (v['avg_belt2'] / v['count'])}
            for k, v in sorted(total_data.items())
        ]

        return Response(output_data)

