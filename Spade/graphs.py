from Spade.database.database import USCDatabaseHelper
import matplotlib.pyplot as plt
import numpy as np


def getDataByYear(all_data) -> dict[str, dict[str, tuple[int, int]]]:
    dataByYear: dict[str, dict[str, tuple[int, int]]] = {}
    for data in all_data:
        currentYear, Object_type, year_total, full_total = data
        if currentYear not in dataByYear:
            dataByYear[currentYear] = {}
        dataByYear[currentYear][Object_type] = (year_total, full_total)

    for year, item in dataByYear.items():
        total_sats = 0
        for object_type in item:
            total_sats += item[object_type][1]
        dataByYear[year]["TOTAL"] = (-1, total_sats)
    return dataByYear


def generateDensityBins(db: USCDatabaseHelper):
    result = db.cursor.execute(
        f"""
        SELECT
            APOAPSIS,
            PERIAPSIS,
            ECCENTRICITY,
            INCLINATION,
            DRY_MASS,
            OBJECT_TYPE
        FROM
            USC
        WHERE
            DRY_MASS IS NOT NULL AND DRY_MASS != ''
            AND APOAPSIS IS NOT NULL AND APOAPSIS != ''
            AND PERIAPSIS IS NOT NULL AND PERIAPSIS != ''
            AND ECCENTRICITY IS NOT NULL AND ECCENTRICITY != ''
            AND INCLINATION IS NOT NULL AND INCLINATION != ''
            AND DRY_MASS IS NOT NULL AND DRY_MASS != ''
            AND OBJECT_TYPE IS NOT NULL AND OBJECT_TYPE != ''
        """
    )
    all_data = result.fetchall()

    # --- 1. Extract and Separate Data by Object Type ---
    payload_altitudes = []
    debris_altitudes = []
    rocket_body_altitudes = []
    total_altitudes = []

    for satellite in all_data:
        try:
            apoapsis = float(satellite[0])
            periapsis = float(satellite[1])
            object_type = satellite[5].strip().upper()

            avg_altitude = (apoapsis + periapsis) / 2
            total_altitudes.append(avg_altitude)

            if "PAYLOAD" in object_type:
                payload_altitudes.append(avg_altitude)
            elif "DEBRIS" in object_type:
                debris_altitudes.append(avg_altitude)
            elif "ROCKET BODY" in object_type:
                rocket_body_altitudes.append(avg_altitude)
        except (ValueError, TypeError):
            continue

    # --- 2. Calculate Spatial Density ---
    # Define constants and bins
    EARTH_RADIUS_KM = 6371
    bins = np.arange(0, 2001, 1)  # 1km altitude bins

    # Calculate frequency (counts) for each bin
    payload_counts, _ = np.histogram(payload_altitudes, bins=bins)
    debris_counts, _ = np.histogram(debris_altitudes, bins=bins)
    rocket_body_counts, _ = np.histogram(rocket_body_altitudes, bins=bins)
    total_counts, bin_edges = np.histogram(total_altitudes, bins=bins)

    # Calculate the volume of each 1km spherical shell
    # V = 4/3 * pi * (r_outer^3 - r_inner^3)
    r_inner = EARTH_RADIUS_KM + bin_edges[:-1]
    r_outer = EARTH_RADIUS_KM + bin_edges[1:]
    shell_volumes = (4.0 / 3.0) * np.pi * (r_outer**3 - r_inner**3)

    # Calculate density = count / volume.
    # Use np.divide for safe division to handle bins with zero volume.
    payload_density = np.divide(
        payload_counts,
        shell_volumes,
        out=np.zeros_like(payload_counts, dtype=float),
        where=shell_volumes != 0,
    )
    debris_density = np.divide(
        debris_counts,
        shell_volumes,
        out=np.zeros_like(debris_counts, dtype=float),
        where=shell_volumes != 0,
    )
    rocket_body_density = np.divide(
        rocket_body_counts,
        shell_volumes,
        out=np.zeros_like(rocket_body_counts, dtype=float),
        where=shell_volumes != 0,
    )
    total_density = np.divide(
        total_counts,
        shell_volumes,
        out=np.zeros_like(total_counts, dtype=float),
        where=shell_volumes != 0,
    )

    # Get the center of each bin for the x-axis
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # --- 3. Plot the Data ---
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot density for each object type
    ax.plot(bin_centers, payload_density, label="Payload", lw=1.5)
    ax.plot(bin_centers, debris_density, label="Debris", lw=1.5)
    ax.plot(bin_centers, rocket_body_density, label="Rocket Body", lw=1.5)
    ax.plot(
        bin_centers,
        total_density,
        label="Total",
        color="black",
        linewidth=2.5,
        zorder=5,
    )

    # --- 4. Customize the Plot ---
    ax.set_title("Spatial Density of Objects by Altitude", fontsize=16)
    ax.set_xlabel("Mean Altitude (km)", fontsize=12)
    ax.set_ylabel("Spatial Density (objects per km³)", fontsize=12)

    # Set the y-axis to a logarithmic scale
    ax.set_yscale("log")

    # Set the y-axis limits as requested
    ax.set_ylim(1e-10, 1e-5)

    ax.set_xlim(0, 2000)
    ax.legend()
    ax.grid(
        True, which="both", linestyle="--", alpha=0.6
    )  # "which='both'" is good for log scales

    plt.tight_layout()

    filename = "./rendered_graphs/DensityLineGraph.png"
    plt.savefig(filename)
    print("saved file for density line graph: ", filename)


def generateAltInc(db: USCDatabaseHelper):
    result = db.cursor.execute(
        f"""
        SELECT
            APOAPSIS,
            PERIAPSIS,
            ECCENTRICITY,
            INCLINATION,
            DRY_MASS
        FROM
            USC
        WHERE
            DRY_MASS IS NOT NULL AND DRY_MASS != ''
            AND APOAPSIS IS NOT NULL AND APOAPSIS != ''
            AND PERIAPSIS IS NOT NULL AND PERIAPSIS != ''
            AND ECCENTRICITY IS NOT NULL AND ECCENTRICITY != ''
            AND INCLINATION IS NOT NULL AND INCLINATION != ''
            AND DRY_MASS IS NOT NULL AND DRY_MASS != ''
        """
    )
    all_data = result.fetchall()

    # PERIAPSIS
    y_APOAPSIS = np.array([float(satellite[0]) for satellite in all_data])
    # PERIAPSIS
    y_PERIAPSIS = np.array([float(satellite[1]) for satellite in all_data])

    # INCLINATION
    y_INCLINATION = np.array([float(satellite[3]) for satellite in all_data])

    fig, ax = plt.subplots(figsize=(10, 7))

    avg_altitude = (y_APOAPSIS + y_PERIAPSIS) / 2

    altitude_bins = np.arange(0, 2001, 1)  # 1km bins from 0 to 2000
    inclination_bins = np.arange(0, 121, 1)  # 1-degree bins from 0 to 120

    # Calculate density (count of points in each 2D bin)
    H, xedges, yedges = np.histogram2d(
        avg_altitude, y_INCLINATION, bins=[altitude_bins, inclination_bins]
    )

    # For each original point, find which bin it belongs to
    x_bin_indices = np.clip(np.digitize(avg_altitude, xedges) - 1, 0, H.shape[0] - 1)
    y_bin_indices = np.clip(np.digitize(y_INCLINATION, yedges) - 1, 0, H.shape[1] - 1)

    # Create the size array based on the density of each point's bin
    s_values = H[x_bin_indices, y_bin_indices] + 5

    # Cap the maximum size of the bubbles
    max_size = 5000
    s_values = np.clip(s_values, a_min=None, a_max=max_size)

    ax.scatter(
        avg_altitude,
        y_INCLINATION,
        s=s_values,
        alpha=0.1,
        color="steelblue",
        edgecolors="none",
        lw=0,
        zorder=3,
    )
    ax.set_xlim(0, 2000)  # Altitude (km)
    ax.set_ylim(0, 120)  # Inclination (degrees)

    ax.set_title("Satellite Inclination vs. Mean Altitude (Density Sized)", fontsize=16)

    ax.set_xlabel("Altitude (km)", fontsize=12)
    ax.set_ylabel("Inclination (degrees)", fontsize=12)

    plt.tight_layout()

    filename = "./rendered_graphs/ScatterALtInc.png"
    plt.savefig(filename)
    print("saved file for scatter plot: ", filename)


def generateScatterGrid(db: USCDatabaseHelper):
    result = db.cursor.execute(
        f"""
        SELECT 
            APOAPSIS,
            PERIAPSIS,
            ECCENTRICITY,
            INCLINATION,
            DRY_MASS
        FROM 
            USC
        WHERE
            DRY_MASS IS NOT NULL AND DRY_MASS != ''
            AND APOAPSIS IS NOT NULL AND APOAPSIS != ''
            AND PERIAPSIS IS NOT NULL AND PERIAPSIS != ''
            AND ECCENTRICITY IS NOT NULL AND ECCENTRICITY != ''
            AND INCLINATION IS NOT NULL AND INCLINATION != ''
            AND DRY_MASS IS NOT NULL AND DRY_MASS != ''
        """
    )
    all_data = result.fetchall()
    x_axis = np.array([satellite_num for satellite_num in range(len(all_data))])

    # PERIAPSIS
    y_APOAPSIS = np.array([satellite[0] for satellite in all_data])

    # PERIAPSIS
    y_PERIAPSIS = np.array([satellite[1] for satellite in all_data])

    # ECCENTRICITY
    y_ECCENTRICITY = np.array([satellite[2] for satellite in all_data])

    # INCLINATION
    y_INCLINATION = np.array([satellite[3] for satellite in all_data])

    # DRY_MASS
    y_MASS = np.array([satellite[4] for satellite in all_data])

    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(10, 7))

    x_indices = range(len(x_axis))

    avg_altitude = (y_APOAPSIS + y_PERIAPSIS) / 2

    # Altitude Graph
    ax1 = axs[0, 0]
    ax1.scatter(
        x_axis,
        avg_altitude,
        color="royalblue",
        zorder=3,
        marker="o",
        s=10,
        label="Mean Altitude",
    )
    ax1.set_ylim(0, 1000)
    ax1.set_title("Satellite Orbital Altitude", fontsize=16)
    ax1.set_ylabel("Altitude (km)", fontsize=12)
    ax1.set_xlabel("")
    ax1.set_xticks([])
    ax1.legend()

    # Eccentricity Graph
    ax2 = axs[0, 1]
    ax2.scatter(
        x_axis,
        y_ECCENTRICITY,
        color="salmon",
        zorder=3,
        marker="o",
        s=10,
        label="Eccentricity",
    )

    ax2.set_title("Satellite Orbital Eccentricity", fontsize=16)
    ax2.set_ylabel("Eccentricity", fontsize=12)
    ax2.set_xlabel("")
    ax2.set_xticks([])
    ax2.legend()

    # Inclination (Deg) Graph
    ax3 = axs[1, 0]
    ax3.scatter(
        x_axis,
        y_INCLINATION,
        color="limegreen",
        zorder=3,
        marker="o",
        s=10,
        label="Inclination",
    )

    ax3.set_title("Satellite Orbital Inclination", fontsize=16)
    ax3.set_ylabel("Inclination (degrees)", fontsize=12)
    ax3.set_xlabel("")
    ax3.set_xticks([])
    ax3.set_ylim(30, 120)
    ax3.legend()

    # mass (kg)
    ax4 = axs[1, 1]
    ax4.scatter(
        x_axis,
        y_MASS,
        color="darkorange",
        zorder=3,
        marker="o",
        s=10,
        label="Mass",
    )

    ax4.set_title("Satellite Mass", fontsize=16)
    ax4.set_ylabel("Mass (kg)", fontsize=12)
    ax4.set_xlabel("")
    ax4.set_xticks([])
    ax4.set_ylim(0, 15000)
    ax4.legend()

    plt.tight_layout()
    filename = "./rendered_graphs/ScatterPlotGRID.png"
    plt.savefig(filename)
    print("saved file for scatter plot: ", filename)


def generateScatterAVG(db: USCDatabaseHelper):
    result = db.cursor.execute(
        f"""
        SELECT 
            APOAPSIS,
            PERIAPSIS,
            ECCENTRICITY,
            INCLINATION,
            DRY_MASS
        FROM 
            USC
        WHERE
            DRY_MASS IS NOT NULL AND DRY_MASS != ''
            AND APOAPSIS IS NOT NULL AND APOAPSIS != ''
            AND PERIAPSIS IS NOT NULL AND PERIAPSIS != ''
            AND ECCENTRICITY IS NOT NULL AND ECCENTRICITY != ''
            AND INCLINATION IS NOT NULL AND INCLINATION != ''
            AND DRY_MASS IS NOT NULL AND DRY_MASS != ''
        """
    )
    all_data = result.fetchall()
    x_axis = np.array([satellite_num for satellite_num in range(len(all_data))])

    # PERIAPSIS
    y_APOAPSIS = np.array([satellite[0] for satellite in all_data])

    # PERIAPSIS
    y_PERIAPSIS = np.array([satellite[1] for satellite in all_data])

    # ECCENTRICITY
    y_ECCENTRICITY = np.array([satellite[2] for satellite in all_data])

    # INCLINATION
    y_INCLINATION = np.array([satellite[3] for satellite in all_data])

    # DRY_MASS
    y_DRY_MASS = np.array([satellite[4] for satellite in all_data])

    fig, ax = plt.subplots(figsize=(10, 7))

    x_indices = range(len(x_axis))

    avg_altitude = (y_APOAPSIS + y_PERIAPSIS) / 2

    ax.scatter(
        x_axis,
        avg_altitude,
        color="royalblue",
        zorder=3,
        marker="o",
        s=10,
        label=r"Mean Altitude ($\bar{x}$)",
    )
    ax.set_ylim(0, 1000)
    ax.set_title("Satellite Orbital Altitude AVG", fontsize=16)
    ax.set_ylabel("Altitude (km)", fontsize=12)
    # ax.set_xticks(x_axis)
    # ax.yaxis.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    plt.tight_layout()

    filename = "./rendered_graphs/ScatterPlotAVG.png"
    plt.savefig(filename)
    print("saved file for scatter plot: ", filename)


def generateScatterPlots(db: USCDatabaseHelper):
    result = db.cursor.execute(
        f"""
        SELECT 
            APOAPSIS,
            PERIAPSIS,
            ECCENTRICITY,
            INCLINATION,
            DRY_MASS
        FROM 
            USC
        WHERE
            DRY_MASS IS NOT NULL AND DRY_MASS != ''
            AND APOAPSIS IS NOT NULL AND APOAPSIS != ''
            AND PERIAPSIS IS NOT NULL AND PERIAPSIS != ''
            AND ECCENTRICITY IS NOT NULL AND ECCENTRICITY != ''
            AND INCLINATION IS NOT NULL AND INCLINATION != ''
            AND DRY_MASS IS NOT NULL AND DRY_MASS != ''
        """
    )
    all_data = result.fetchall()
    x_axis = np.array([satellite_num for satellite_num in range(len(all_data))])

    # PERIAPSIS
    y_APOAPSIS = np.array([satellite[0] for satellite in all_data])

    # PERIAPSIS
    y_PERIAPSIS = np.array([satellite[1] for satellite in all_data])

    # ECCENTRICITY
    y_ECCENTRICITY = np.array([satellite[2] for satellite in all_data])

    # INCLINATION
    y_INCLINATION = np.array([satellite[3] for satellite in all_data])

    # DRY_MASS
    y_DRY_MASS = np.array([satellite[4] for satellite in all_data])

    fig, ax = plt.subplots(figsize=(10, 7))

    x_indices = range(len(x_axis))

    ax.vlines(
        x=x_indices,
        ymin=y_PERIAPSIS,
        ymax=y_APOAPSIS,
        color="grey",
        alpha=0.7,
        linewidth=2,
        label="Orbital Altitude Range",
    )

    ax.scatter(
        x_axis,
        y_APOAPSIS,
        color="dodgerblue",
        zorder=1,
        marker="^",
        s=10,
        label="Apoapsis",
    )

    ax.scatter(
        x_axis,
        y_PERIAPSIS,
        color="orangered",
        zorder=3,
        marker="v",
        s=10,
        label="Periapsis",
    )
    ax.set_ylim(0, 1000)
    ax.set_title("Satellite Orbital Altitude Range", fontsize=16)
    ax.set_ylabel("Altitude (km)", fontsize=12)
    # ax.set_xticks(x_axis)
    # ax.yaxis.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    plt.tight_layout()

    filename = "./rendered_graphs/ScatterPlot.png"
    plt.savefig(filename)
    print("saved file for scatter plot: ", filename)


def generateSatellitesOvertime(db: USCDatabaseHelper):
    print("Generating graph")
    result = db.cursor.execute(
        f"""
        WITH YearlyCounts AS (
            SELECT 
                strftime('%Y', DEBUT) as LAUNCH_YEAR,
                OBJECT_TYPE, 
                COUNT(*) as TYPE_COUNT
            FROM 
                USC
            WHERE
                DEBUT IS NOT NULL AND DEBUT != ''
                AND OBJECT_TYPE IS NOT NULL AND OBJECT_TYPE != ''
            GROUP BY 
                LAUNCH_YEAR, OBJECT_TYPE
        )

        SELECT
            LAUNCH_YEAR,
            OBJECT_TYPE,
            TYPE_COUNT,
            SUM(TYPE_COUNT) OVER (
                PARTITION BY OBJECT_TYPE
                ORDER BY LAUNCH_YEAR
            ) as CUMULATIVE_COUNT
        FROM
            YearlyCounts
        ORDER BY
            LAUNCH_YEAR, OBJECT_TYPE

        """
    )
    all_data = result.fetchall()

    starlinkResult = db.cursor.execute(
        f"""
        WITH StarLinkCounts AS (
            SELECT
                strftime('%Y', DEBUT) as LAUNCH_YEAR,
                OBJECT_TYPE,
                COUNT(*) as TYPE_COUNT
            FROM
                USC
            WHERE
                DEBUT IS NOT NULL AND DEBUT != ''
                AND OBJECT_TYPE IS NOT NULL AND OBJECT_TYPE != ''
                AND SATELLITE_NAME LIKE 'STARLINK%'
            GROUP BY
                LAUNCH_YEAR, OBJECT_TYPE
        )

        SELECT
            LAUNCH_YEAR,
            OBJECT_TYPE,
            TYPE_COUNT,
            SUM(TYPE_COUNT) OVER (
                PARTITION BY OBJECT_TYPE
                ORDER BY LAUNCH_YEAR
            ) as CUMULATIVE_COUNT
        FROM
            StarLinkCounts
        ORDER BY
            LAUNCH_YEAR, OBJECT_TYPE

        """
    )

    dataByYear = getDataByYear(all_data)
    # print(dataByYear)
    starlinkByYear = getDataByYear(starlinkResult.fetchall())
    # Plot Total
    x_total = np.array([int(year) for year in dataByYear])
    y_total = np.array(
        [dataByYear[year].get("TOTAL", (0, 0))[1] for year in dataByYear]
    )

    # Debris Total
    x_Debris = np.array([int(year) for year in dataByYear])
    y_Debris = np.array(
        [dataByYear[year].get("DEBRIS", (0, 0))[1] for year in dataByYear]
    )

    # ROCKET BODY Total
    x_ROCKET_BODY = np.array([int(year) for year in dataByYear])
    y_ROCKET_BODY = np.array(
        [dataByYear[year].get("ROCKET BODY", (0, 0))[1] for year in dataByYear]
    )

    # PAYLOAD Total
    x_PAYLOAD = np.array([int(year) for year in dataByYear])
    y_PAYLOAD = np.array(
        [dataByYear[year].get("PAYLOAD", (0, 0))[1] for year in dataByYear]
    )

    # Starlink Total
    x_STARLINK = np.array([int(year) for year in starlinkByYear])
    y_STARLINK = np.array(
        [starlinkByYear[year].get("PAYLOAD", (0, 0))[1] for year in starlinkByYear]
    )
    # print(x_STARLINK)
    # print(y_STARLINK)

    min_year = 1955
    max_year = max(x_total)
    # Generate tick locations from min_year to max_year with a step of 5
    tick_interval = 5
    xticks_locations = np.arange(min_year, max_year + tick_interval, tick_interval)

    plt.figure(figsize=(10, 6))
    plt.title("Cumulative Objects in Orbit by Type")
    plt.plot(x_total, y_total, label="Total", linewidth=3)
    plt.plot(x_PAYLOAD, y_PAYLOAD, label="Payload", linewidth=3)
    plt.plot(x_Debris, y_Debris, label="Debris", linewidth=3)
    plt.plot(x_ROCKET_BODY, y_ROCKET_BODY, label="Rocket Body", linewidth=3)

    # Starlink line: normal size and different style
    plt.plot(x_STARLINK, y_STARLINK, label="Starlink", linewidth=2, linestyle="--")

    starlink_year = 2019
    starlink_y = starlinkByYear[str(starlink_year)]["PAYLOAD"][1]

    # Annotation for first starlink launch
    plt.annotate(
        "First Starlink launch\nMay 2019",
        xy=(starlink_year, starlink_y),
        xytext=(starlink_year - 20, starlink_y - 15),
        arrowprops=dict(
            arrowstyle="->",
            color="black",
            lw=1.2,
            connectionstyle="arc3,rad=-0.3",
        ),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.8),
        ha="left",
        va="top",
        fontsize=9,
    )

    y1, y2 = 2006, 2007

    d1 = dataByYear[str(y1)]["DEBRIS"][1]
    d2 = dataByYear[str(y2)]["DEBRIS"][1]

    # midpoint coords between 2006-2007
    x_mid = 0.5 * (y1 + y2)
    y_mid = 0.5 * (d1 + d2)

    # Annotation for Chinese Anti-Satellite Missile Test
    plt.annotate(
        "Chinese anti-satellite\nmissile test\nJan 2007",
        xy=(x_mid, y_mid),  # arrow tip
        xytext=(x_mid - 20, y_mid + 15),
        arrowprops=dict(
            arrowstyle="->",
            color="black",
            lw=1.2,
            connectionstyle="arc3,rad=0.2",
        ),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.8),
        ha="center",
        va="top",
        fontsize=9,
    )

    y1, y2 = 2008, 2009

    d1 = dataByYear[str(y1)]["DEBRIS"][1]
    d2 = dataByYear[str(y2)]["DEBRIS"][1]

    # midpoint coords between 2006-2007
    x_mid = 0.5 * (y1 + y2)
    y_mid = 0.5 * (d1 + d2)

    # Annotation for Iridium 33 and Kosmos 2251 collision
    plt.annotate(
        "Iridium 33 & Kosmos 2251\ncollision\nFeb 2009",
        xy=(x_mid, y_mid),
        xytext=(-90, 60),
        textcoords="offset points",
        ha="center",
        va="top",
        arrowprops=dict(arrowstyle="->", lw=1.2, connectionstyle="arc3,rad=0.2"),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.8),
        fontsize=9,
    )

    plt.xlabel("Year")
    plt.ylabel("Cumulative Count of Objects")
    plt.grid(True, linestyle="--", alpha=0.7)

    plt.tight_layout()
    plt.legend()
    plt.xticks(xticks_locations)
    filename = "./rendered_graphs/Cumulative_Objects_in_Orbit_by_Type.png"
    plt.savefig(filename)

    print(f"Plot saved to {filename}")
