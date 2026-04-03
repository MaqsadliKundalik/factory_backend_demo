from typing import TYPE_CHECKING

from django.db import models
from apps.common.models import BaseModel
from utils.sayqal import SayqalSms

if TYPE_CHECKING:
    from data.orders.models import Order
    from data.files.models import File
    from data.whouse.models import Whouse

sayqal = SayqalSms()


class Client(BaseModel):
    name = models.CharField(max_length=255)
    inn_number = models.CharField(max_length=9)

    address = models.CharField(max_length=512, null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    mfo = models.CharField(max_length=20, null=True, blank=True)
    oked = models.CharField(max_length=20, null=True, blank=True)
    director = models.CharField(max_length=255, null=True, blank=True)

    contract = models.CharField(max_length=255, null=True, blank=True)

    photo: "File | None" = models.ForeignKey(
        "files.File", on_delete=models.SET_NULL, null=True, blank=True
    )
    whouse: "Whouse" = models.ForeignKey(
        "factory_whouse.Whouse", on_delete=models.CASCADE
    )

    list_display = ["name", "inn_number", "whouse", "files"]

    orders: "models.QuerySet[Order]"
    branches: "models.QuerySet[ClientBranches]"
    phones: "models.QuerySet[ClientPhone]"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # TODO: inn number branchesda va bu modelda unique bo'lishi kerak
        existing = Client.objects.filter(inn_number=self.inn_number).exclude(id=self.id)
        if existing.exists():
            raise ValueError("Client with this INN number already exists")
        existing_branch = ClientBranches.objects.filter(inn=self.inn_number).exclude(client_id=self.id)
        if existing_branch.exists():
            raise ValueError("Client branch with this INN number already exists")

    def send_sms(self, message: str):
        for phone in self.phones.all():
            res = sayqal.send_sms(phone.phone_number, message)
            status = sayqal.status_sms(res.transactionid, res.smsid)
            if status.status == 5:
                print("Unsupported template\n\n{msg}".format(msg=message))
        print("\n\n\n{status}\n\n{msg}\n\n\n".format(status=status.status, msg=message))


class ClientBranches(BaseModel):
    client: "Client" = models.ForeignKey(
        "clients.Client", on_delete=models.CASCADE, related_name="branches"
    )
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    longitude = models.FloatField()
    latitude = models.FloatField()

    bank_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    mfo = models.CharField(max_length=20, null=True, blank=True)
    oked = models.CharField(max_length=20, null=True, blank=True)
    inn = models.CharField(max_length=20, null=True, blank=True)
    director = models.CharField(max_length=255, null=True, blank=True)
    contract = models.CharField(max_length=255, null=True, blank=True)

    list_display = ["client", "name", "address", "longitude", "latitude"]

    def __str__(self):
        return f"{self.name} - {self.client}"

    class Meta:
        unique_together = ["client", "longitude", "latitude"]


class ClientPhone(BaseModel):
    client: "Client" = models.ForeignKey(
        "clients.Client", on_delete=models.CASCADE, related_name="phones"
    )
    phone_number = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)

    list_display = ["client", "phone_number", "name", "role"]

    def __str__(self):
        return f"{self.phone_number} - {self.name} - {self.role}"

    def save(self, *args, **kwargs):
        # Check if this is an existing record with the same phone number
        if self.pk:
            existing = ClientPhone.objects.filter(
                pk=self.pk,
                client=self.client,
                phone_number=self.phone_number
            ).first()
            if existing:
                # If the phone number is the same, skip unique validation
                super().save(*args, **kwargs)
                return
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ["client", "phone_number"]
