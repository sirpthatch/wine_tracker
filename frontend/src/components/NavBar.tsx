import { NavLink } from "react-router-dom";

export function NavBar() {
  return (
    <nav className="nav">
      <NavLink to="/" className="nav-brand">
        🍷 Wine Tracker
      </NavLink>
      <div className="nav-links">
        <NavLink
          to="/"
          end
          className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
        >
          My Wines
        </NavLink>
        <NavLink
          to="/suggestions"
          className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
        >
          Suggestions
        </NavLink>
      </div>
    </nav>
  );
}
