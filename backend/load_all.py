from backend import charging_station_dataloader
from backend import diesel_price_dataloader
from backend import elec_price_dataloader
from backend import electric_vehicle_data_loader
from backend import gas_price_dataloader
from backend import new_evcar_dataloader
from backend import total_vehicle_data_loader


def run():
    print("=== 전체 데이터 로딩 시작 ===")

    charging_station_dataloader.run()
    gas_price_dataloader.run()
    diesel_price_dataloader.run()
    elec_price_dataloader.run()
    electric_vehicle_data_loader.run()
    new_evcar_dataloader.run()
    total_vehicle_data_loader.run()

    print("=== 전체 데이터 로딩 완료 ===")


if __name__ == "__main__":
    run()