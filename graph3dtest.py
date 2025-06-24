import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import math as m

# --- Physical Constants ---
# Earth's standard gravitational parameter (mu or GM) in km^3/s^2
EARTH_GRAVITATIONAL_PARAMETER = 398600.4418
# Earth's mean radius in kilometers, for plotting the wireframe.
EARTH_RADIUS_KM = 6371
# Number of seconds in one sidereal day, used for mean motion conversion.
SECONDS_PER_SIDEREAL_DAY = 24 * 3600 * 0.997269


def parse_epoch_from_tle(tle_line1):
    """
    Parses the epoch (date and time) from TLE Line 1.

    Args:
        tle_line1 (str): The first line of a TLE pair.

    Returns:
        datetime.datetime: A datetime object representing the TLE epoch.
    """
    tle_two_digit_year = int(tle_line1[18:20])
    current_two_digit_year = dt.date.today().year % 100
    year_prefix = "19" if tle_two_digit_year > current_two_digit_year else "20"

    day_of_year = tle_line1[20:23]
    fractional_day = float(tle_line1[23:33])

    total_hours = 24 * fractional_day
    hours = int(total_hours)
    total_minutes = (total_hours % 1) * 60
    minutes = int(total_minutes)
    seconds = int((total_minutes % 1) * 60)

    date_str = (
        f"{year_prefix}{tle_two_digit_year} {day_of_year} {hours} {minutes} {seconds}"
    )
    return dt.datetime.strptime(date_str, "%Y %j %H %M %S")


def parse_orbital_elements(tle_line2):
    """
    Parses the core orbital elements from TLE Line 2.

    Args:
        tle_line2 (str): The second line of a TLE pair.

    Returns:
        dict: A dictionary containing the satellite's name and key orbital elements.
    """
    return {
        "name": tle_line2[2:7].strip(),
        "inclination_rad": m.radians(float(tle_line2[9:17])),
        "raan_rad": m.radians(float(tle_line2[17:26])),
        "eccentricity": float("." + tle_line2[26:34]),
        "arg_of_perigee_rad": m.radians(float(tle_line2[34:43])),
        "mean_motion_rev_per_day": float(tle_line2[52:63]),
    }


# Half of the length of its longest diameter
def calculate_semi_major_axis(mean_motion_rev_per_day):
    """
    Calculates the semi-major axis from the mean motion using Kepler's Third Law.

    Args:
        mean_motion_rev_per_day (float): Revolutions per day.

    Returns:
        float: The semi-major axis in kilometers.
    """
    mean_motion_rad_per_sec = (
        mean_motion_rev_per_day * 2 * m.pi
    ) / SECONDS_PER_SIDEREAL_DAY
    return (EARTH_GRAVITATIONAL_PARAMETER / (mean_motion_rad_per_sec**2)) ** (1.0 / 3)


def calculate_ellipse_properties(semi_major_axis, eccentricity):
    """
    Calculates derived properties of the orbital ellipse.

    Args:
        semi_major_axis (float): The semi-major axis (a) in km.
        eccentricity (float): The eccentricity (e) of the orbit.

    Returns:
        dict: A dictionary with the semi-minor axis (b) and focal distance (c).
    """
    semi_minor_axis = semi_major_axis * m.sqrt(1 - eccentricity**2)
    focal_distance = semi_major_axis * eccentricity
    return {"semi_minor_axis": semi_minor_axis, "focal_distance": focal_distance}


def compute_rotation_matrix(raan_rad, inclination_rad, arg_of_perigee_rad):
    """
    Computes the combined 3D rotation matrix to orient the orbit in space.

    Args:
        raan_rad (float): Right Ascension of the Ascending Node in radians.
        inclination_rad (float): Inclination in radians.
        arg_of_perigee_rad (float): Argument of Perigee in radians.

    Returns:
        numpy.ndarray: The 3x3 rotation matrix.
    """
    R_raan = np.array(
        [
            [m.cos(raan_rad), -m.sin(raan_rad), 0],
            [m.sin(raan_rad), m.cos(raan_rad), 0],
            [0, 0, 1],
        ]
    )
    R_inclination = np.array(
        [
            [1, 0, 0],
            [0, m.cos(inclination_rad), -m.sin(inclination_rad)],
            [0, m.sin(inclination_rad), m.cos(inclination_rad)],
        ]
    )
    R_arg_perigee = np.array(
        [
            [m.cos(arg_of_perigee_rad), -m.sin(arg_of_perigee_rad), 0],
            [m.sin(arg_of_perigee_rad), m.cos(arg_of_perigee_rad), 0],
            [0, 0, 1],
        ]
    )
    return np.matmul(np.matmul(R_raan, R_inclination), R_arg_perigee)


def generate_orbit_points(orbit_params, rotation_matrix):
    """
    Generates the x, y, z coordinates for the orbital path.

    Args:
        orbit_params (dict): A dictionary containing all orbital parameters.
        rotation_matrix (numpy.ndarray): The 3x3 rotation matrix for the orbit.

    Returns:
        tuple: Three lists (x_coords, y_coords, z_coords) for the orbit path.
    """
    x_coords, y_coords, z_coords = [], [], []
    for angle in np.linspace(0, 2 * m.pi, 100):
        # Point on an ellipse in its 2D plane, centered at the origin
        p_local = np.array(
            [
                [orbit_params["semi_major_axis"] * m.cos(angle)],
                [orbit_params["semi_minor_axis"] * m.sin(angle)],
                [0],
            ]
        )
        # Shift the ellipse so the focus (Earth) is at the origin
        p_shifted = p_local - np.array([[orbit_params["focal_distance"]], [0], [0]])
        # Rotate the point to its correct orientation in 3D space
        p_rotated = np.matmul(rotation_matrix, p_shifted)
        x_coords.append(p_rotated[0][0])
        y_coords.append(p_rotated[1][0])
        z_coords.append(p_rotated[2][0])
    return x_coords, y_coords, z_coords


def plot_earth(ax):
    """
    Plots a wireframe sphere representing the Earth on the given axes.

    Args:
        ax: A matplotlib 3D axes object.
    """
    u, v = np.mgrid[0 : 2 * np.pi : 20j, 0 : np.pi : 10j]
    x = EARTH_RADIUS_KM * np.cos(u) * np.sin(v)
    y = EARTH_RADIUS_KM * np.sin(u) * np.sin(v)
    z = EARTH_RADIUS_KM * np.cos(v)
    ax.plot_wireframe(x, y, z, color="b", alpha=0.5, lw=0.5, zorder=0)


def customize_plot(fig, ax, num_orbits, last_epoch_time):
    """
    Applies final customizations to the plot (title, labels, legend, etc.).

    Args:
        fig: The matplotlib figure object.
        ax: The matplotlib 3D axes object.
        num_orbits (int): The number of orbits plotted, for legend placement.
        last_epoch_time (datetime.datetime): The epoch of the last plotted orbit.
    """
    ax.set_xlabel("X-axis (km)")
    ax.set_ylabel("Y-axis (km)")
    ax.set_zlabel("Z-axis (km)")
    ax.xaxis.set_tick_params(labelsize=7)
    ax.yaxis.set_tick_params(labelsize=7)
    ax.zaxis.set_tick_params(labelsize=7)
    ax.set_aspect("equal", adjustable="box")

    if last_epoch_time:
        title = "Satellite Orbits (ECI Frame) as of " + last_epoch_time.strftime(
            "%B %d, %Y"
        )
        ax.set_title(title)

    if num_orbits < 5:
        ax.legend()
    else:
        fig.subplots_adjust(right=0.8)
        ax.legend(loc="center left", bbox_to_anchor=(1.07, 0.5), fontsize=7)


def generate_orbit_visualization(tle_data_lines, output_filename):
    """
    Main function to generate and save a 3D visualization of satellite orbits.
    This function orchestrates the parsing, calculation, and plotting steps.

    Args:
        tle_data_lines (list of str): Raw lines from a TLE file.
        output_filename (str): The filename for the saved plot (e.g., "orbits.png").
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(projection="3d", computed_zorder=False)
    last_epoch = None
    num_orbits = len(tle_data_lines) // 2

    # --- Step 1: Process each TLE pair and plot its orbit ---
    for i in range(num_orbits):
        tle_line1 = tle_data_lines[i * 2].strip()
        tle_line2 = tle_data_lines[i * 2 + 1].strip()

        if tle_line1[0] != "1":
            print(f"Warning: Skipping invalid TLE pair at line {i * 2 + 1}.")
            continue

        # Get the time the orbit data is valid for
        last_epoch = parse_epoch_from_tle(tle_line1)

        # Get the satellite's orbital parameters (shape, orientation, etc.)
        orbit_params = parse_orbital_elements(tle_line2)

        # Calculate the size of the orbit (semi-major axis)
        orbit_params["semi_major_axis"] = calculate_semi_major_axis(
            orbit_params["mean_motion_rev_per_day"]
        )

        # Calculate the specific shape of the ellipse
        ellipse_props = calculate_ellipse_properties(
            orbit_params["semi_major_axis"], orbit_params["eccentricity"]
        )
        orbit_params.update(ellipse_props)

        # Get the rotation needed to orient the orbit in 3D space
        rotation_matrix = compute_rotation_matrix(
            orbit_params["raan_rad"],
            orbit_params["inclination_rad"],
            orbit_params["arg_of_perigee_rad"],
        )

        # Generate the 3D points for the orbital path
        x, y, z = generate_orbit_points(orbit_params, rotation_matrix)

        # Plot the orbit
        ax.plot(x, y, z, zorder=5, label=orbit_params["name"])

    # --- Step 2: Add the Earth to the plot for context ---
    plot_earth(ax)

    # --- Step 3: Finalize the plot with titles, labels, and a legend ---
    customize_plot(fig, ax, num_orbits, last_epoch)

    # --- Step 4: Save the final visualization to a file ---
    plt.savefig(output_filename, dpi=300)
    print(f"Plot saved successfully as '{output_filename}'.")


if __name__ == "__main__":
    TLE_FILE_PATH = "tle.txt"
    OUTPUT_FILENAME = "satellite_orbits.png"

    try:
        with open(TLE_FILE_PATH, "r") as f:
            loaded_tle_lines = f.readlines()
        generate_orbit_visualization(loaded_tle_lines, OUTPUT_FILENAME)
    except FileNotFoundError:
        print(f"Error: The file '{TLE_FILE_PATH}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
