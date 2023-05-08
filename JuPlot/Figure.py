from PlotBackend import * 
from DataStructures import Backend, Theme, ThemeElement

class Figure:
    __backends = {Backend.matplotlib: MatplotlibBackend,
                  Backend.plotly: PlotlyBackend,
                  Backend.empty: EmptyBackend
                }

    def __init__(self, *args, **kwargs):
        self.__backend = self.__backends[kwargs.get('backend', Backend.empty)](*args, **kwargs)

    def change_backend(self, backend: Backend, *args, **kwargs): self.__backend = PlotBackend.migrate_backend(self.__backend, self.__backends[backend], *args, **kwargs)

    def plot(self, *args, **kwargs): self.__backend.plot(*args, **kwargs)

    def show(self, *args, **kwargs): self.__backend.show(*args, **kwargs)

    def set_theme_param(self, *args, **kwargs): self.__backend.set_theme_param(*args, **kwargs)

    def get_theme(self): return self.__backend.theme

    def save_theme(self, path): return self.__backend.theme.save(path)

    def set_theme(self, theme): self.__backend.theme = theme

    def set_theme_json(self, path): self.__backend.theme = Theme.load(path)

    def reset_theme(self): self.__backend.reset_theme()

    def get_figure(self): return self.__backend.figure

    def get_history(self): return self.__backend.history

    def get_current_plot(self): return self.__backend.current_plot

    def redo_plot(self, *args, **kwargs): self.__backend.redo_plot(*args, **kwargs)

    # def backend_actions(self, action, *args, **kwargs): self.__backend.actions(action, *args, **kwargs)