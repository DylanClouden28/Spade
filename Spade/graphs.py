from Spade.database import USCDatabaseHelper
import matplotlib.pyplot as plt
import numpy as np


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

    print(dataByYear)
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

    min_year = 1955
    max_year = max(x_total)
    # Generate tick locations from min_year to max_year with a step of 5
    tick_interval = 5
    xticks_locations = np.arange(min_year, max_year + tick_interval, tick_interval)

    filename = "my_plot.png"
    plt.plot(x_total, y_total, label="Total")  # Added label
    plt.plot(x_PAYLOAD, y_PAYLOAD, label="Payload")  # Added label
    plt.plot(x_Debris, y_Debris, label="Debris")  # Added label
    plt.plot(x_ROCKET_BODY, y_ROCKET_BODY, label="Rocket Body")  # Added label
    plt.tight_layout()
    plt.legend()
    plt.xticks(xticks_locations)
    plt.savefig(filename)

    print(f"Plot saved to {filename}")
