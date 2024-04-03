# import asyncio
from RCS.rcs import RCSBatchCapabilityTask, RCSDataForCheck
from RCS.task import dummy
# from client.client import main3


if __name__ == '__main__':
    data = RCSBatchCapabilityTask(task_id='1', data=[
        RCSDataForCheck(country='UK', msisdns=['+447359388306', '+447359388305']),
        RCSDataForCheck(country='RU', msisdns=['+447359388305']),
        RCSDataForCheck(country='ENG', msisdns=['+447359388304']),
        RCSDataForCheck(country='BR', msisdns=['+447359388303']),
                                                     ])
    result = dummy.delay(data.dict())
    # asyncio.run(main3())
