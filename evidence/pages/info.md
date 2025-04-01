# Information

Inspired by this [YouTube Video](https://www.youtube.com/watch?v=U16a8tdrbII), I calculate the [Elo ratings](https://en.wikipedia.org/wiki/Elo_rating_system) for all F1 drivers.

## Elo Rating System in F1: A Race-Based Approach

Unlike the linked video, where Elo ratings were based on within-team matches, I calculate Elo ratings by race. This approach treats each Grand Prix as a standalone event where every driver-constructor pairing competes against all others.

### How it Works:

1.  **Race as a "Match":** In this model, a race acts as a single event, where all driver-constructor pairings go head-to-head against each other and play a "match". The final Elo ratings are based on the average Elo results for all head-to-head matches for a race.
2.  **Head-to-Head Comparisons:** For each race, every driver's finishing position is compared against every other driver's position.
3.  **Win/Loss Determination:** If a driver finishes ahead of another driver, it's considered a "win" in their head-to-head match. Conversely, finishing behind another driver is a "loss."
4.  **Elo Adjustment:** The Elo rating of each driver is adjusted after each race based on the outcomes of these head-to-head matches. The magnitude of the adjustment depends on the difference in Elo ratings between the two drivers and the outcome of the match.
5. **Averaging Driver and Constructor Elo:** In order to account for the driver-constructor pairing, the Elo scores for the driver and the constructor are averaged together when calculating the Elo score. This means that a driver's performance is not only based on their own skill, but also the performance of the car they are driving.
6. **Elo Carry Over:** Elo ratings are calculated at the end of each race, and Elo ratings are pushed forward to the following races. This means that a driver's performance in one race will affect their Elo rating in the next race.

### Example:

For example, if a driver ends the race in 5th position out of 12 drivers, they have lost 4 matches with drivers who placed ahead of them and won 7 matches against drivers who placed behind them. These wins and losses are then used to adjust the driver's Elo rating.

### Key Differences from Traditional Elo:

*   **Multi-Player Matches:** Traditional Elo is designed for two-player games. This system adapts it to multi-player races.
*   **Race-Centric:** Instead of focusing on individual duels, the focus is on the overall race outcome.
*   **Constructor Influence:** The Elo rating is a combination of the driver's skill and the constructor's performance.

## Project Details

### Data Source:

The dataset used for this project is available on [Motherduck](https://motherduck.com). It contains comprehensive F1 race results, driver information, and constructor data.

### Accessing the Data:

Download the dataset using this share:

```Code
-- Run this snippet to attach database
ATTACH 'md:_share/F1_Results/2c252e3d-f9a1-4ab1-93e1-328d84b6347b';
