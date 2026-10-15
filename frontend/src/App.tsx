
import { useState } from "react";
import "./App.css";

type TravelRequest = {
  origin: string;
  destination: string;
  departure_date: string;
  return_date: string;
  passengers: number;
  cabin_class: "economy" | "premium_economy" | "business" | "first";
  max_budget: number;
  max_stops: number;
  hotel_min_rating: number;
};

type TravelOption = {
  flight: {
    airline: string;
    flight_number: string;
    origin: string;
    destination: string;
    departure_time: string;
    arrival_time: string;
    cabin_class: string;
    price: number;
    stops: number;
    duration_hours: number;
  };
  hotel: {
    name: string;
    city: string;
    rating: number;
    nightly_price: number;
    currency: string;
    address?: string | null;
  };
  nights: number;
  flight_cost: number;
  hotel_cost: number;
  total_cost: number;
  remaining_budget: number;
  budget: number;
};

type TravelPlanResponse = {
  message: string;
  travel_request: TravelRequest;
  recommendation_count: number;
  recommendations: TravelOption[];
  explanation: string;
};

const initialRequest: TravelRequest = {
  origin: "London",
  destination: "New York",
  departure_date: "",
  return_date: "",
  passengers: 1,
  cabin_class: "business",
  max_budget: 2500,
  max_stops: 1,
  hotel_min_rating: 4,
};

function App() {
  const [request, setRequest] = useState<TravelRequest>(initialRequest);
  const [results, setResults] = useState<TravelPlanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Sorting and budget-filter state must be inside App()
  const [sortBy, setSortBy] = useState("total_price");
  const [withinBudgetOnly, setWithinBudgetOnly] = useState(false);


  const cheapestTotal = results && results.recommendations.length > 0
    ? Math.min(
        ...results.recommendations.map((option) => option.total_cost),
      )
    : null;
  const displayedRecommendations = (results?.recommendations ?? [])
  .filter(
    (option) =>
      !withinBudgetOnly || option.total_cost <= request.max_budget,
  )
  .sort((a, b) => {
    switch (sortBy) {
      case "flight_price":
        return a.flight_cost - b.flight_cost;
      case "hotel_rating":
        return b.hotel.rating - a.hotel.rating;
      case "fewest_stops":
        return (
          a.flight.stops - b.flight.stops ||
          a.total_cost - b.total_cost
        );
      case "total_price":
      default:
        return a.total_cost - b.total_cost;
    }
  });
  function updateField<K extends keyof TravelRequest>(
    field: K,
    value: TravelRequest[K],
  ) {
    setRequest((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResults(null);

    try {
      const response = await fetch("http://127.0.0.1:8001/travel/plan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      const data: unknown = await response.json();

      if (!response.ok) {
        const detail =
          typeof data === "object" &&
          data !== null &&
          "detail" in data
            ? JSON.stringify(data.detail)
            : `Request failed with status ${response.status}`;

        throw new Error(detail);
      }

      setResults(data as TravelPlanResponse);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to the travel API.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <header className="hero">
        <p className="eyebrow">AI-POWERED TRAVEL PLANNING</p>
        <h1>Find your next journey.</h1>
        <p>Compare flight and hotel combinations that fit your budget.</p>
      </header>

      <form className="travel-form" onSubmit={handleSubmit}>
        <h2>Plan your trip</h2>

        <div className="form-grid">
          <label>
            Origin
            <input
              value={request.origin}
              onChange={(e) => updateField("origin", e.target.value)}
              minLength={2}
              required
            />
          </label>

          <label>
            Destination
            <input
              value={request.destination}
              onChange={(e) => updateField("destination", e.target.value)}
              minLength={2}
              required
            />
          </label>

          <label>
            Departure date
            <input
              type="date"
              value={request.departure_date}
              onChange={(e) => updateField("departure_date", e.target.value)}
              required
            />
          </label>

          <label>
            Return date
            <input
              type="date"
              min={request.departure_date || undefined}
              value={request.return_date}
              onChange={(e) => updateField("return_date", e.target.value)}
              required
            />
          </label>

          <label>
            Passengers
            <input
              type="number"
              min={1}
              max={20}
              value={request.passengers}
              onChange={(e) => updateField("passengers", Number(e.target.value))}
              required
            />
          </label>

          <label>
            Cabin class
            <select
              value={request.cabin_class}
              onChange={(e) =>
                updateField(
                  "cabin_class",
                  e.target.value as TravelRequest["cabin_class"],
                )
              }
            >
              <option value="economy">Economy</option>
              <option value="premium_economy">Premium economy</option>
              <option value="business">Business</option>
              <option value="first">First class</option>
            </select>
          </label>

          <label>
            Maximum budget (£)
            <input
              type="number"
              min={1}
              step="0.01"
              value={request.max_budget}
              onChange={(e) => updateField("max_budget", Number(e.target.value))}
              required
            />
          </label>

                <label>
                  Maximum flight stops
                  <select
                    value={request.max_stops}
                    onChange={(e) => updateField("max_stops", Number(e.target.value))}
                  >
                    {[0, 1, 2, 3, 4, 5].map((stops) => (
                      <option key={stops} value={stops}>
                        {stops === 0 ? "Non-stop only" : `Up to ${stops} stops`}
                      </option>
                    ))}
                  </select>
                </label>

               <label>
                  Minimum hotel rating
                  <select
                    value={request.hotel_min_rating}
                    onChange={(e) =>
                    updateField("hotel_min_rating", Number(e.target.value))
                    }
                  >
                  {[1, 2, 3, 4, 4.5, 5].map((rating) => (
                    <option key={rating} value={rating}>
                      {rating}+ stars
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <button className="search-button" type="submit" disabled={loading}>
              {loading ? "Finding travel options..." : "Find travel options"}
             </button>
          </form>

          {error && (
            <section className="travel-form" role="alert">
              <h2>Travel search failed</h2>
              <p>{error}</p>
              <p>Check that FastAPI and the MCP server are running.</p>
            </section>
          )}

          {results && (
              <section className="results">
              <h2>Your travel options</h2>
              <p>{results.message}</p>
              <p>
                {results.recommendation_count} combinations returned. Demo prices
                only; not live quotes.
              </p>
              <div className="result-controls">
                <label>
                  Sort by
                  <select value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
                    <option value="total_price">Lowest total price</option>
                    <option value="flight_price">Lowest flight price</option>
                    <option value="hotel_rating">Highest hotel rating</option>
                    <option value="fewest_stops">Fewest flight stops</option>
                  </select>
                </label>

                <label className="budget-filter">
                  <input type="checkbox" checked={withinBudgetOnly} onChange={(event) => setWithinBudgetOnly(event.target.checked)} />
                    Show only options within my budget (£
                      {request.max_budget.toFixed(2)})
                </label>
              </div>

              <p>
                Showing {displayedRecommendations.length} of{" "}
                {results.recommendation_count} recommendations.
              </p>
              {displayedRecommendations.length === 0 && (
                <article className="travel-form empty-state">
                  <h3>No matching travel options</h3>
                  <p>
                    {results.recommendations.length === 0
                    ? "The travel planner returned no recommendations for this request."
                    : "No recommendations match your current filters."}
                  </p>
                  <p>Try increasing your budget or changing your travel preferences.</p>
                </article>
              )}
                {displayedRecommendations.length > 0 &&
                  displayedRecommendations.map((option, index) => (
                  <article
                    className="travel-form result-card"
                      key={`${option.flight.flight_number}-${option.hotel.name}-${index}`}
                  >
                  {option.total_cost === cheapestTotal && (
                     <p className="best-value">CHEAPEST OPTION</p>
                 )}
              


              <h3>
                Option {index + 1}: {option.flight.airline}
              </h3>
              <p>
                {option.flight.origin} → {option.flight.destination}
              </p>
              <p>
                 Flight {option.flight.flight_number} ·{" "}
                 {option.flight.stops} stop(s) ·{" "}
                 {option.flight.duration_hours} hours
              </p>
              <p>
                Departure: {option.flight.departure_time} ·{" "}
                Arrival: {option.flight.arrival_time}
              </p>
              <p>Cabin class: {option.flight.cabin_class}</p>
              <hr />
              <h3>{option.hotel.name}</h3>
              <p>
                {option.hotel.rating} stars · {option.nights} nights
              </p>
              {option.hotel.address && <p>Address: {option.hotel.address}</p>}
              <p>
                Nightly rate: £{option.hotel.nightly_price.toFixed(2)}
              </p>
              <p>Flight: £{option.flight_cost.toFixed(2)}</p>
              <p>Hotel: £{option.hotel_cost.toFixed(2)}</p>
              <h3>Total: £{option.total_cost.toFixed(2)}</h3>
              <p>Remaining budget: £{option.remaining_budget.toFixed(2)}</p>
            </article>
          ))}

          <article className="travel-form">
            <h3>AI travel explanation</h3>
            <p>{results.explanation}</p>
          </article>
        </section>
      )}
    </main>
  );
}

export default App;