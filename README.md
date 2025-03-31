# F1_Elo

This project calculates and tracks Elo ratings for Formula 1 drivers and teams.

## Features

*   **Elo Rating Calculation:** Implements the Elo rating system to rank drivers and teams based on race results.
*   **Data Management:** Stores and manages driver, team, and race data.
*   **Historical Tracking:** Tracks Elo ratings over time, providing insights into performance trends.
*   **Data Visualization**: Provides a way to visualize the data.

## Getting Started

### Prerequisites

*   Python 3.10
*   Dependencies are managed using `uv`

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    ```
2.  Install dependencies:
    ```bash
    uv sync
    ```

### Usage

1.  Run the main script:
    ```bash
    cd etl
    uv run python etl.py
    uv run pyton calculate_elo.py
    uv run python update_md.py
    ```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is licensed under the MIT License.
