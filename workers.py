import settings 

class SeleniumWorkers:


    def __init__(self, selenium_setup, num_workers = settings.WORKERS) -> None:
        self.num_workers = num_workers
        self.setup_func = selenium_setup


    def set_num_workers(self, num: int) -> None:
        if num >= 100:
            print("Limit the number of workers")
        self.num_workers = num
    

    def get_num_workers(self):
        return self.num_workers

    
    def setup_workers(self):
        drivers = [self.setup_func() for _ in range(settings.WORKERS)]
        return drivers


    def teardown_workers(drivers: list):
        [driver.quit() for driver in drivers]