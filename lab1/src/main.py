from entities.inventory.cosmetics import Cosmetics
from entities.inventory.hairdressing_equipment import HairdressingEquipment
from entities.management.client import Client
from entities.management.master import Master
from entities.salon import Salon
from entities.services.hair_service import HairService
from entities.services.service import Service
from utils.masters_specialization import MastersSpecialization

Milana = Salon("Milana")

nozhnicy = HairdressingEquipment("Nozhnicy", "", 5)
pomada = Cosmetics("Pomada", 10, "", 10)
Milana.add_to_inventory(pomada)
Milana.add_to_inventory(nozhnicy)

Ilya = Master("Ilya", 25, MastersSpecialization.COSMETICS)
Milana.hire_staff(Ilya)

classic_cut = HairService("Classic cut", 40, "Side part", [nozhnicy])
Milana.add_service(classic_cut)

guest = Client("Alex", 20)

try:
    booking = Milana.make_booking(
        client=guest,
        master=Ilya,
        service=classic_cut
    )
    print("Success")
except Exception as e:
    print(f"Error: {e}")

print(Milana.check_balance())
print(nozhnicy.get_condition())
# nozhnicy.degrade()
# nozhnicy.degrade()

Milana.complete_booking(booking)
print(guest.get_hair_service_status(),guest.get_cosmetic_status())

print(Milana.check_balance())
print(nozhnicy.get_condition())

# print("balance: ", Milana.check_balance())
# print("amount of pomada: ", pomada.get_amount())
#
# Milana.sell_product("Pomada", 1)
#
# print("balance: ", Milana.check_balance())
# print("amount of pomada: ", pomada.get_amount())