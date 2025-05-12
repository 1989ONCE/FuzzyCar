import os
import sys
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from car import Car
from fuzzy import fuzzy_steering, simple_control, draw_mfGraph

class gui():
    def __init__(self, app_name, app_width, app_height):
        self.track = []
        self.path_result = []
        self.ax = None
        self.mfax = None
        self.car_artists = []
        self.path_artists = []
        self.position_artists = []
        self.model = None

        # container initialization
        self.container = tk.Tk()
        self.container.config(bg='white', padx=10, pady=10)
        self.container.maxsize(app_width, app_height)
        self.container.title(app_name)
        self.container.geometry(str(app_width) + 'x' + str(app_height))

        # components initialization
        self.setting_frame = tk.Frame(self.container, width=500, height=450, bg='white')
        self.graph_frame = tk.Frame(self.container, width=1300, height=450, bg='white')


        self.track_graph = FigureCanvasTkAgg(master = self.graph_frame)
        self.track_graph.get_tk_widget().config(width=430, height=400)

        self.mf_graph = FigureCanvasTkAgg(master = self.container)
        self.mf_graph.get_tk_widget().config(width=800, height=750)

        # components placing
        self.setting_frame.place(x=5, y=5)
        self.graph_frame.place(x=5, y=100)
        self.track_graph.get_tk_widget().place(x=0, y=10)
        self.mf_graph.get_tk_widget().place(x=450, y=0)

        self.figure = None
        self.fuzzyMF_figure = None

        self.run_simple_btn = tk.Button(
            master=self.setting_frame,  
            command=lambda: self.run_fuzzy('simple_control'), 
            height=2,  
            width=15, 
            text="For testing",
            highlightbackground='white'
        )
        self.run_fuzzy_btn = tk.Button(
            master=self.setting_frame,  
            command=lambda: self.run_fuzzy('fuzzy_control'), 
            height=2,  
            width=15, 
            text="Run Fuzzy Control",
            highlightbackground='white'
        )
       
        self.run_simple_btn.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.run_fuzzy_btn.grid(row=0, column=1, padx=5, pady=5, sticky='w')


        self.draw_car_track() # Draw track
        self.fuzzyMF_figure = draw_mfGraph() # Draw fuzzy membership function graph
        # Show the plot in the GUI
        self.mf_graph.figure = self.fuzzyMF_figure
        self.mf_graph.draw()
    
    def open(self):
        self.container.mainloop()

    def check_finish(self, epoch=None):
        if 18 <= self.car.currentX <= 30 and 37 <= self.car.currentY:
            if epoch == '-':
                self.container.after(0, lambda: messagebox.showinfo('Success', 'Car has reached the finish!'))
            elif epoch is not None:
                self.container.after(0, lambda: messagebox.showinfo('Success', f'Car has reached the finish at Epoch {epoch+1}!'))
            
            return True
        return False

    def clear_car_artists(self):
        if len(self.car_artists) > 0:
            for artist in self.car_artists:
                if artist is not None:
                    artist.remove()
            self.car_artists = []

    def clear_position_artists(self):
        if len(self.position_artists) > 0:
            for artist in self.position_artists:
                if artist is not None:
                    artist.remove()
            self.position_artists = []

    def clear_path_artists(self):
        if len(self.path_artists) > 0:
            for artist in self.path_artists:
                if artist is not None:
                    artist.remove()
            self.path_artists = []

    def draw_car_track(self):
        if hasattr(sys, '_MEIPASS'):
            trackFile = os.path.join(sys._MEIPASS, "track.txt")
        else:
            trackFile = os.path.join(os.path.abspath("."), "track.txt")

        with open(trackFile, 'r') as f:
            lines = f.readlines()
        
        # “起點座標”及“起點與水平線之的夾角”
        start_x, start_y, phi = [float(coord) for coord in lines[0].strip().split(',')]

        # “終點區域左上角座標”及“終點區域右下角座標”
        finish_top_left = [float(coord) for coord in lines[1].strip().split(',')]
        finish_bottom_right = [float(coord) for coord in lines[2].strip().split(',')]
        
        # “賽道邊界”
        boundaries = [[float(coord) for coord in line.strip().split(',')] for line in lines[3:]]
        
        # Extract x and y coordinates from boundaries
        boundary_x, boundary_y = zip(*boundaries)
        self.track = boundaries
        self.car = Car(start_x, start_y, phi, boundaries)

        # print('boundaries', boundaries)
        self.figure = plt.Figure(figsize=(15, 15), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(-20, 40)
        self.ax.set_ylim(-5, 55)
        self.ax.set_aspect('equal') # 讓xy軸的單位長度相等
        self.ax.set_title("Track")

        # Plot track boundary
        self.ax.plot(boundary_x, boundary_y, 'k-', linewidth=2)

        # Draw start line
        self.ax.plot([-6, 6], [0, 0], 'b-', linewidth=2, label="Start Line")

        # Draw finishing line
        self.ax.plot([18, 30], [37, 37], 'k-', linewidth=2, label="Finishing Line")
        self.ax.plot([18, 30], [40, 40], 'k-', linewidth=2)
        
        
        num_squares = 10 # Number of squares each rows
        square_width = (finish_bottom_right[0] - finish_top_left[0]) / num_squares
        square_height = (finish_bottom_right[1] - finish_top_left[1]) / 2
        
        for row in range(2):
            for i in range(num_squares):
                color = 'black' if (i + row) % 2 == 0 else 'white'
                self.ax.add_patch(plt.Rectangle((finish_top_left[0] + i * square_width, finish_top_left[1] + row * square_height),
                        square_width, square_height,
                        edgecolor=color, facecolor=color))

        # Draw starting position and direction arrow
        car, text, path = self.car.draw_car(self.ax)
        self.position_artists.append(car)
        self.position_artists.append(text)
        self.path_artists.append(path)
        self.ax.plot(start_x, start_y, 'ro', label="Start Position")
        self.ax.scatter([], [], color='darkgrey', label='Path')
        self.ax.scatter([], [], marker=r'$\rightarrow$', label=f"Front Sensor", color='red', s=100)
        self.ax.scatter([], [], marker=r'$\rightarrow$', label=f"Right Sensor", color='blue', s=100)
        self.ax.scatter([], [], marker=r'$\rightarrow$', label=f"Left Sensor", color='green', s=100)
        # Set chart properties
        self.ax.set_aspect('equal')
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_title("Track")
        self.ax.legend()
        plt.grid(True)

        # Show plot
        self.track_graph.figure = self.figure
        self.track_graph.draw()
        
    def run_fuzzy(self, control_type):
        self.clear_car_artists()
        self.clear_path_artists()

        self.car = Car(0, 0, 90, self.track)  # 重置車輛
        self.run_fuzzy_btn.config(state='disabled')
        self.run_simple_btn.config(state='disabled')

        try:
            result_list = []  # Initialize result_list here
            done = False
            while not done:
                distances = self.car.get_distances()
                if control_type == 'simple_control':
                    theta = simple_control(distances[1], distances[2])
                else:
                    # Fuzzy control
                    # Calculate the steering angle using fuzzy logic
                    theta = fuzzy_steering(distances[0], distances[1], distances[2])
                    result_list.append(theta)
                self.car.set_currentTHETA(theta)
                self.car.update_position()

                self.clear_car_artists()
                self.clear_position_artists()
                self.car_artists.append(self.car.draw_sensor_distance_arrow(self.ax, 'Front', self.car.currentX, self.car.currentY, self.car.currentPHI, distances[0]))
                self.car_artists.append(self.car.draw_sensor_distance_arrow(self.ax, 'Left', self.car.currentX, self.car.currentY, self.car.currentPHI + 45, distances[1]))
                self.car_artists.append(self.car.draw_sensor_distance_arrow(self.ax, 'Right', self.car.currentX, self.car.currentY, self.car.currentPHI - 45, distances[2]))

                car, text, center = self.car.draw_car(self.ax)
                self.position_artists.append(car)
                self.position_artists.append(text)
                self.path_artists.append(center)

                self.track_graph.get_tk_widget().update()
                self.track_graph.draw()

                if self.check_finish('-'):
                    done = True
                elif self.car.check_collision():
                    messagebox.showinfo("Collision", "Car hit the wall!")
                    done = True
        except Exception as e:
            print(f"Error in run_fuzzy: {e}")
        finally:
            self.run_fuzzy_btn.config(state='normal')
            self.run_simple_btn.config(state='normal')
            # save the theta result to ' result.txt'
            if len(result_list) > 0:
                if hasattr(sys, '_MEIPASS'):
                    resultFile = os.path.join(sys._MEIPASS, "result.txt")
                else:
                    resultFile = os.path.join(os.path.abspath("."), "result.txt")
                with open(resultFile, 'w') as f:
                    for result in result_list:
                        f.write(f"{result}\n")