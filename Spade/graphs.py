from Spade.database import USCDatabaseHelper
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
