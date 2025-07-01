import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import math as m

from Spade.database import USCDatabaseHelper

# --- Physical Constants ---
# Earth's standard gravitational parameter (mu or GM) in km^3/s^2
EARTH_GRAVITATIONAL_PARAMETER = 398600.4418
# Earth's mean radius in kilometers, for plotting the wireframe.
EARTH_RADIUS_KM = 6371
# Number of seconds in one sidereal day, used for mean motion conversion.
SECONDS_PER_SIDEREAL_DAY = 24 * 3600 * 0.997269


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
        p_local = np.array(
            [
                [orbit_params["semi_major_axis"] * m.cos(angle)],
                [orbit_params["semi_minor_axis"] * m.sin(angle)],
                [0],
            ]
        )
        p_shifted = p_local - np.array([[orbit_params["focal_distance"]], [0], [0]])
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


def customize_plot(fig, ax, num_orbits, last_epoch_time, title=None):
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
        title = (
            title
            if title
            else "Satellite Orbits (ECI Frame) as of "
            + last_epoch_time.strftime("%B %d, %Y")
        )
        ax.set_title(title)

    if num_orbits < 5:
        ax.legend()
    else:
        fig.subplots_adjust(right=0.8)
        ax.legend(loc="center left", bbox_to_anchor=(1.05, 0.5), fontsize=7)


def plot_orbits_from_data(
    satellite_data: list[tuple[str, str, float, float, float, float, float]],
    output_filename: str,
    title: str | None = None,
    dpi: int = 300,
    line_width: float = 1,
    legend_data: dict[str, str] | None = None,
):
    """
    Generates and saves a 3D visualization of satellite orbits.

    This function is designed to take data directly from a database query result.
    It expects the `satellite_data` to be a list of tuples, with each tuple
    containing the following 7 elements in order:
    1. Satellite Name (str)
    2. Epoch (datetime.datetime or compatible string)
    3. Inclination (float, in degrees)
    4. RAAN (float, in degrees)
    5. Eccentricity (float)
    6. Argument of Perigee (float, in degrees)
    7. Mean Motion (float, in revolutions per day)

    Args:
        satellite_data (list of tuples): The data for the satellites to plot.
        output_filename (str): The filename for the saved plot.
        title (str | None, optional): The main title for the plot. Defaults to None.
        dpi (int, optional): The resolution of the saved image. Defaults to 300.
        line_width (float, optional): The width of the orbit lines. Defaults to 1.
        legend_data (dict[str, str] | None, optional): A dictionary mapping
            satellite names to additional string information to be displayed
            in the legend. Example: {"ISS (ZARYA)": "Mass: 420t"}.
            Defaults to None.
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(projection="3d", computed_zorder=False)
    last_epoch = None

    for satellite_tuple in satellite_data:
        (
            name,
            epoch,
            inclination_deg,
            raan_deg,
            eccentricity,
            arg_of_perigee_deg,
            mean_motion_rev_per_day,
        ) = satellite_tuple

        try:
            format_code = "%Y-%m-%d %H:%M:%S.%f"
            last_epoch = datetime.strptime(epoch, format_code)
        except ValueError:
            print(
                f"Error converting {epoch} from str into datetime object, did not match format {format_code}. Skipping."
            )
            continue

        orbit_params = {
            "name": name,
            "eccentricity": eccentricity,
            "inclination_rad": m.radians(inclination_deg),
            "raan_rad": m.radians(raan_deg),
            "arg_of_perigee_rad": m.radians(arg_of_perigee_deg),
        }

        orbit_params["semi_major_axis"] = calculate_semi_major_axis(
            mean_motion_rev_per_day
        )
        ellipse_props = calculate_ellipse_properties(
            orbit_params["semi_major_axis"], orbit_params["eccentricity"]
        )
        orbit_params.update(ellipse_props)

        rotation_matrix = compute_rotation_matrix(
            orbit_params["raan_rad"],
            orbit_params["inclination_rad"],
            orbit_params["arg_of_perigee_rad"],
        )

        x, y, z = generate_orbit_points(orbit_params, rotation_matrix)

        # --- CHANGE START ---
        # Construct the label for the legend. If legend_data is provided
        # and contains the satellite's name, append the extra info.
        label = orbit_params["name"]
        if legend_data and name in legend_data:
            label = f"{label} ({legend_data[name]})"
        # --- CHANGE END ---

        ax.plot(x, y, z, zorder=5, label=label, linewidth=line_width)

    plot_earth(ax)
    customize_plot(fig, ax, len(satellite_data), last_epoch, title=title)
    plt.savefig(output_filename, dpi=dpi, bbox_inches="tight")
    print(f"Plot saved successfully as '{output_filename}'.")


def generate3dgraphsOrbits(db: USCDatabaseHelper):

    #
    # Random test satellites
    #
    result = db.cursor.execute(
        f"""
	    SELECT
	        NORAD_CAT_ID,
	        SATELLITE_NAME,
	        EPOCH,
	        INCLINATION,
	        RA_OF_ASC_NODE,
	        ECCENTRICITY,
	        ARG_OF_PERIGEE,
	        MEAN_MOTION
	    FROM
	        USC
	    WHERE
	        NORAD_CAT_ID = '12679' OR NORAD_CAT_ID = '19478'
	    """
    )
    all_data = result.fetchall()
    input_data = [item[1:] for item in all_data]
    OUTPUT_FILENAME = "satellite_orbits_from_db.png"
    try:
        plot_orbits_from_data(input_data, OUTPUT_FILENAME)
    except Exception as e:
        print(f"An unexpected error occurred during plotting: {e}")

    #
    # STARLINK
    #
    result = db.cursor.execute(
        f"""
	    SELECT
	        NORAD_CAT_ID,
	        SATELLITE_NAME,
	        EPOCH,
	        INCLINATION,
	        RA_OF_ASC_NODE,
	        ECCENTRICITY,
	        ARG_OF_PERIGEE,
	        MEAN_MOTION
	    FROM
	        USC
	    WHERE
	        SATELLITE_NAME LIKE '%STARLINK%'
	        AND EPOCH IS NOT NULL
	        AND INCLINATION IS NOT NULL
	        AND RA_OF_ASC_NODE IS NOT NULL
	        AND ECCENTRICITY IS NOT NULL
	        AND ARG_OF_PERIGEE IS NOT NULL
	        AND MEAN_MOTION IS NOT NULL
	    """
    )
    all_data = result.fetchall()
    input_data = [item[1:] for item in all_data]
    OUTPUT_FILENAME = "satellite_orbits_from_db_starlink.png"
    try:
        plot_orbits_from_data(
            input_data,
            OUTPUT_FILENAME,
            title="Orbits of Starlink Satellites",
            dpi=1000,
            line_width=0.1,
        )
    except Exception as e:
        print(f"An unexpected error occurred during plotting: {e}")

    #
    # KUIPER
    #
    result = db.cursor.execute(
        f"""
	    SELECT
	        NORAD_CAT_ID,
	        SATELLITE_NAME,
	        EPOCH,
	        INCLINATION,
	        RA_OF_ASC_NODE,
	        ECCENTRICITY,
	        ARG_OF_PERIGEE,
	        MEAN_MOTION
	    FROM
	        USC
	    WHERE
	        SATELLITE_NAME LIKE '%KUIPER%'
	        AND EPOCH IS NOT NULL
	        AND INCLINATION IS NOT NULL
	        AND RA_OF_ASC_NODE IS NOT NULL
	        AND ECCENTRICITY IS NOT NULL
	        AND ARG_OF_PERIGEE IS NOT NULL
	        AND MEAN_MOTION IS NOT NULL
	    """
    )
    all_data = result.fetchall()
    input_data = [item[1:] for item in all_data]
    OUTPUT_FILENAME = "satellite_orbits_from_db_kuiper.png"
    try:
        plot_orbits_from_data(
            input_data, OUTPUT_FILENAME, title="Orbits of Kuiper Satellites"
        )
    except Exception as e:
        print(f"An unexpected error occurred during plotting: {e}")

    #
    # OneWeb
    #
    result = db.cursor.execute(
        f"""
	    SELECT
	        NORAD_CAT_ID,
	        SATELLITE_NAME,
	        EPOCH,
	        INCLINATION,
	        RA_OF_ASC_NODE,
	        ECCENTRICITY,
	        ARG_OF_PERIGEE,
	        MEAN_MOTION
	    FROM
	        USC
	    WHERE
	        SATELLITE_NAME LIKE '%OneWeb%'
	        AND EPOCH IS NOT NULL
	        AND INCLINATION IS NOT NULL
	        AND RA_OF_ASC_NODE IS NOT NULL
	        AND ECCENTRICITY IS NOT NULL
	        AND ARG_OF_PERIGEE IS NOT NULL
	        AND MEAN_MOTION IS NOT NULL
	    """
    )
    all_data = result.fetchall()
    input_data = [item[1:] for item in all_data]
    OUTPUT_FILENAME = "satellite_orbits_from_db_oneweb.png"
    try:
        plot_orbits_from_data(
            input_data,
            OUTPUT_FILENAME,
            title="Orbits of OneWeb Satellites",
            dpi=500,
            line_width=1,
        )
    except Exception as e:
        print(f"An unexpected error occurred during plotting: {e}")

    #
    # ViaSat
    #
    result = db.cursor.execute(
        f"""
	    SELECT
	        NORAD_CAT_ID,
	        SATELLITE_NAME,
	        EPOCH,
	        INCLINATION,
	        RA_OF_ASC_NODE,
	        ECCENTRICITY,
	        ARG_OF_PERIGEE,
	        MEAN_MOTION
	    FROM
	        USC
	    WHERE
	        SATELLITE_NAME LIKE '%VIASAT%'
	        AND EPOCH IS NOT NULL
	        AND INCLINATION IS NOT NULL
	        AND RA_OF_ASC_NODE IS NOT NULL
	        AND ECCENTRICITY IS NOT NULL
	        AND ARG_OF_PERIGEE IS NOT NULL
	        AND MEAN_MOTION IS NOT NULL
	    """
    )
    all_data = result.fetchall()
    input_data = [item[1:] for item in all_data]
    OUTPUT_FILENAME = "satellite_orbits_from_db_viasat.png"
    try:
        plot_orbits_from_data(
            input_data,
            OUTPUT_FILENAME,
            title="Orbits of ViaSat Satellites",
            line_width=0.1,
            dpi=500,
        )
    except Exception as e:
        print(f"An unexpected error occurred during plotting: {e}")

    #
    # Top 10 sats by mass
    #
    result = db.cursor.execute(
        f"""
	    SELECT
	        NORAD_CAT_ID,
	        SATELLITE_NAME,
	        EPOCH,
	        INCLINATION,
	        RA_OF_ASC_NODE,
	        ECCENTRICITY,
	        ARG_OF_PERIGEE,
	        MEAN_MOTION,
	        DRY_MASS
	    FROM
	        USC
	    WHERE
	        EPOCH IS NOT NULL
	        AND INCLINATION IS NOT NULL
	        AND RA_OF_ASC_NODE IS NOT NULL
	        AND ECCENTRICITY IS NOT NULL
	        AND ARG_OF_PERIGEE IS NOT NULL
	        AND MEAN_MOTION IS NOT NULL
	        AND DRY_MASS IS NOT NULL
	    ORDER BY
	        DRY_MASS DESC
	    LIMIT
	        10
	    """
    )
    all_data = result.fetchall()
    plot_data = [item[1:8] for item in all_data]
    legend_info = {row[1]: f"Mass: {row[8]:.0f} kg" for row in all_data}
    OUTPUT_FILENAME = "satellite_orbits_from_top10_mass.png"
    try:
        plot_orbits_from_data(
            plot_data,
            OUTPUT_FILENAME,
            title="Orbits of Top 10 Heaviest Satellites",
            legend_data=legend_info,
        )
    except Exception as e:
        print(f"An unexpected error occurred during plotting: {e}")

    #
    # --- MODIFIED BLOCK: Top 10 lightest sats ---
    #
    result = db.cursor.execute(
        f"""
	    SELECT
	        NORAD_CAT_ID,
	        SATELLITE_NAME,
	        EPOCH,
	        INCLINATION,
	        RA_OF_ASC_NODE,
	        ECCENTRICITY,
	        ARG_OF_PERIGEE,
	        MEAN_MOTION,
	        DRY_MASS
	    FROM
	        USC
	    WHERE
	        EPOCH IS NOT NULL
	        AND INCLINATION IS NOT NULL
	        AND RA_OF_ASC_NODE IS NOT NULL
	        AND ECCENTRICITY IS NOT NULL
	        AND ARG_OF_PERIGEE IS NOT NULL
	        AND MEAN_MOTION IS NOT NULL
	        AND DRY_MASS IS NOT NULL
	    ORDER BY
	        DRY_MASS ASC
	    LIMIT
	        10
	    """
    )
    all_data = result.fetchall()

    # Prepare data for the plot and the legend
    plot_data = [item[1:8] for item in all_data]
    legend_info = {row[1]: f"Mass: {row[8]:.2f} kg" for row in all_data}

    # Define the output filename for the plot
    OUTPUT_FILENAME = "satellite_orbits_from_db_10_light_mass.png"

    # Call the main function with the mock data
    try:
        plot_orbits_from_data(
            plot_data,
            OUTPUT_FILENAME,
            title="Orbits of Top 10 Lightest Satellites",
            legend_data=legend_info,
        )
    except Exception as e:
        print(f"An unexpected error occurred during plotting: {e}")

    #
    # --- MODIFIED BLOCK: Top 10 highest eccentricity ---
    #
    result = db.cursor.execute(
        f"""
	    SELECT
	        NORAD_CAT_ID,
	        SATELLITE_NAME,
	        EPOCH,
	        INCLINATION,
	        RA_OF_ASC_NODE,
	        ECCENTRICITY,
	        ARG_OF_PERIGEE,
	        MEAN_MOTION
	    FROM
	        USC
	    WHERE
	        EPOCH IS NOT NULL
	        AND INCLINATION IS NOT NULL
	        AND RA_OF_ASC_NODE IS NOT NULL
	        AND ECCENTRICITY IS NOT NULL
	        AND ARG_OF_PERIGEE IS NOT NULL
	        AND MEAN_MOTION IS NOT NULL
	    ORDER BY
	        ECCENTRICITY DESC
	    LIMIT
	        10
	    """
    )
    all_data = result.fetchall()

    # Prepare data for the plot and the legend
    # Column 1 is SATELLITE_NAME, Column 5 is ECCENTRICITY
    plot_data = [item[1:] for item in all_data]
    legend_info = {row[1]: f"Ecc: {row[5]:.4f}" for row in all_data}

    # Define the output filename for the plot
    OUTPUT_FILENAME = "satellite_orbits_from_db_high_ecc.png"

    # Call the main function with the mock data
    try:
        plot_orbits_from_data(
            plot_data,
            OUTPUT_FILENAME,
            title="Orbits of Top 10 Satellites by Greatest Eccentricity",
            legend_data=legend_info,
        )
    except Exception as e:
        print(f"An unexpected error occurred during plotting: {e}")

    # #
    # # All the satellites
    # #
    # result = db.cursor.execute(
    #     f"""
    #     SELECT
    #         NORAD_CAT_ID,
    #         SATELLITE_NAME,
    #         EPOCH,
    #         INCLINATION,
    #         RA_OF_ASC_NODE,
    #         ECCENTRICITY,
    #         ARG_OF_PERIGEE,
    #         MEAN_MOTION
    #     FROM
    #         USC
    #     WHERE
    #         EPOCH IS NOT NULL
    #         AND INCLINATION IS NOT NULL
    #         AND RA_OF_ASC_NODE IS NOT NULL
    #         AND ECCENTRICITY IS NOT NULL
    #         AND ARG_OF_PERIGEE IS NOT NULL
    #         AND MEAN_MOTION IS NOT NULL
    #     """
    # )
    # all_data = result.fetchall()
    # # print(all_data)

    # input_data = [item[1:] for item in all_data]

    # # Define the output filename for the plot
    # OUTPUT_FILENAME = "satellite_orbits_from_db_all_of_them.png"

    # # Call the main function with the mock data
    # try:
    #     plot_orbits_from_data(
    #         input_data,
    #         OUTPUT_FILENAME,
    #         title="Orbits of All Satellites with Available Data",
    #         line_width=0.1,
    #         dpi=2000,
    #     )
    # except Exception as e:
    #     print(f"An unexpected error occurred during plotting: {e}")
