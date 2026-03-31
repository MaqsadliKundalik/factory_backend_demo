import os
import re
import hashlib
import time

from dataclasses import dataclass
from random import randint

from requests import post


@dataclass
class SendSmsResponse:

    transactionid: int

    smsid: int
    parts: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            transactionid=data["transactionid"],
            smsid=data["smsid"],
            parts=data["parts"],
        )

    def to_dict(self) -> dict:
        return {
            "transactionid": self.transactionid,
            "smsid": self.smsid,
            "parts": self.parts,
        }


@dataclass
class SmsStatusResponse:
    smsid: str
    status: int
    statusdate: str
    parts: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            smsid=data["smsid"],
            status=data["status"],
            statusdate=data["statusdate"],
            parts=data["parts"],
        )


class SayqalSms:
    def __init__(self, username=None, token=None):

        self.username = username
        self.token = token

        if self.username is None:

            self.username = os.getenv("SAYQAL_USERNAME")
        if self.token is None:
            self.token = os.getenv("SAYQAL_TOKEN")

        assert (
            self.username is not None
        ), "Environment variable SAYQAL_USERNAME is not set"

        assert self.token is not None, "Environment variable SAYQAL_TOKEN is not set"

        self.url = "https://routee.sayqal.uz/sms/"

    def generateToken(self, method: str, utime: int):

        access = f"{method} {self.username} {self.token} {utime}"
        token = hashlib.md5(access.encode()).hexdigest()

        return token

    def fixNumber(self, number: str):
        number = re.sub(r'[\s\-\(\)]', '', str(number))
        if number.startswith("+"):
            return number[1:]
        return number

    def send_sms(self, number: str, message: str):

        utime = int(time.time())

        token = self.generateToken("TransmitSMS", utime)

        number = self.fixNumber(number)

        url = self.url + "TransmitSMS"

        data = {
            "utime": utime,
            "username": self.username,
            "service": {"service": 2},
            "message": {
                "smsid": randint(111111, 999999),
                "phone": number,
                "text": message,
            },
        }

        response = post(url, json=data, headers={"X-Access-Token": token})

        return SendSmsResponse.from_dict(response.json())

    def status_sms(self, transaction_id: int, smsid: int) -> SmsStatusResponse:
        utime = int(time.time())
        token = self.generateToken("StatusSMS", utime)

        url = self.url + "StatusSMS"

        data = {
            "utime": utime,
            "username": self.username,
            "transactionid": transaction_id,
            "smsid": smsid,
        }

        response = post(url, json=data, headers={"X-Access-Token": token})

        # --- HARD FAIL if not JSON ---
        try:
            payload = response.json()
        except Exception:
            raise RuntimeError(f"Invalid JSON response: {response.text}")

        # --- Handle by status code ---
        if response.status_code == 200:
            return SmsStatusResponse.from_dict(payload)

        elif response.status_code == 400:
            raise RuntimeError(
                f"SMS API error {payload['errorCode']}: {payload['errMsg']}"
            )

        elif response.status_code == 403:
            raise PermissionError("Invalid token (403 from SMS API)")

        else:
            raise RuntimeError(f"Unexpected status {response.status_code}: {payload}")
