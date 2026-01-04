# ICS Filter Proxy

This add-on fetches an upstream ICS feed and republishes filtered ICS calendars for Home Assistant. It exposes two filtered calendars on port `8099`:

- `http://<HA-IP>:8099/glyn_year7.ics`
- `http://<HA-IP>:8099/glyn_term_dates.ics`

## Installation

1. In Home Assistant, open **Settings > Add-ons > Add-on Store**.
2. Click the **three dots** menu and choose **Repositories**.
3. Add this repository URL and click **Add**.
4. Find **ICS Filter Proxy** in the add-on list and click **Install**.
5. Open the add-on, adjust the **Upstream URL** option if needed, and click **Start**.

## Configuration

- **Upstream URL** (`upstream_url`): The ICS feed to fetch. Defaults to `https://www.glynschool.org/calendar/events.ics`.

## Usage

After starting the add-on, add the filtered calendars in Home Assistant by creating new calendar integrations pointing to:

- `http://<HA-IP>:8099/glyn_year7.ics`
- `http://<HA-IP>:8099/glyn_term_dates.ics`

The add-on automatically filters events according to the Year 7 and term-date rules before serving them to Home Assistant.
