from collections import namedtuple
from datetime import datetime, timedelta
from enum import Enum, unique
from struct import Struct

import base64
import six


@unique
class ContractType(Enum):
    legacy = 0
    standard = 1
    bronze = 2
    silver = 3
    gold = 4
    freenascertified = 5
    freenasmini = 6


@unique
class ContractHardware(Enum):
    parts = 0
    nextday = 1
    fourhour = 2


@unique
class ContractSoftware(Enum):
    none = 0
    business = 1
    integral = 2


@unique
class Features(Enum):
    dedup = 1
    jails = 2
    fiberchannel = 3


license_v1_struct = Struct(
    'b'  # Version
    '16s'  # Model
    '16s'  # System Serial
    '16s'  # System Serial (HA)
    'b'  # Contract Type
    'b'  # Contract Software (Legacy)
    'b'  # Contract Hardware (Legacy)
    '8s'  # Date in string format yyyymmdd
    'Q'  # Contract duration (days)
    '32s'  # Customer Name
    '32s'  # Customer Key
    'L'  # Enabled Features
    'b'  # Number of additional hardware
)
license_v1_addhw = Struct(
    'b'  # Number/quantity of the hardware
    'b'  # Type/identifier of the hardware
)

LicenseBase = namedtuple(
    'LicenseBase',
    'version model system_serial system_serial_ha contract_type '
    'contract_hardware contract_software contract_start duration '
    'customer_name customer_key features addhw'
)


class License(LicenseBase):

    @property
    def contract_end(self):
        return self.contract_start + timedelta(days=self.duration)

    @property
    def expired(self):
        return self.contract_end < datetime.now().date()

    @classmethod
    def load(cls, data):
        data = base64.b64decode(data)

        unpack = list(license_v1_struct.unpack(data[:license_v1_struct.size]))

        unpack[1] = unpack[1].decode('ascii').strip('\x00')
        unpack[2] = unpack[2].decode('ascii').strip('\x00')
        unpack[3] = unpack[3].decode('ascii').strip('\x00')

        unpack[7] = datetime.strptime(
            unpack[7].decode('ascii'), '%Y%m%d'
        ).date()

        features = []
        for f in Features:
            if f.value & unpack[11]:
                features.append(f)
        unpack[11] = features


        # Unpack remainder of the data related to the additional hardware
        addhw = []
        hwremainder = data[license_v1_struct.size:]
        for step in range(unpack[-1]):
            addhw.append(
                license_v1_addhw.unpack(hwremainder[step*2:(step + 1) * 2])
            )

        unpack[-1] = addhw

        return cls._make(unpack)

    def dump(self):
        features = 0
        for f in self.features:
            features |= f.value

        pack = license_v1_struct.pack(
            self.version,
            six.b(self.model),
            six.b(self.system_serial),
            six.b(self.system_serial_ha),
            self.contract_type.value,
            self.contract_hardware.value,
            self.contract_software.value,
            six.b(self.contract_start.strftime("%Y%m%d")),
            self.duration,
            six.b(self.customer_name),
            six.b(self.customer_key),
            features,
            len(self.addhw),
        )

        # Pack additional hardware into the license
        for num, hwtype in self.addhw:
            pack += license_v1_addhw.pack(num, hwtype)

        return base64.b64encode(pack)


if __name__ == '__main__':
    dump = License(version=1, model='Z50', system_serial='A1-3333333333333', system_serial_ha='', duration=300, features=[Features.dedup], contract_type=ContractType.bronze, contract_hardware=ContractHardware.parts, contract_software=ContractSoftware.none, contract_start=datetime.today().date(), customer_name='', customer_key='', addhw=[(5, 1)]).dump()
    with open('license.key', 'wb+') as f:
        f.write(dump)
        print(License.load(dump))
