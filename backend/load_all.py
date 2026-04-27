from backend.Loaders import charging_station_dataloader
from backend.Loaders import diesel_price_dataloader
from backend.Loaders import elec_price_dataloader
from backend.Loaders import electric_vehicle_data_loader
from backend.Loaders import gas_price_dataloader
from backend.Loaders import new_evcar_dataloader
from backend.Loaders import total_vehicle_data_loader


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