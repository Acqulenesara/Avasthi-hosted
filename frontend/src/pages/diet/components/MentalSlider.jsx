export default function MentalSlider({ icon, label, name, value, onChange }) {
  return (
    <div className="mental-slider">
      <div className="mental-header">
        <span className="mental-icon">{icon}</span>
        <span className="mental-label">{label}</span>
        <span className="mental-value">{value}</span>
      </div>

      <input
        type="range"
        min="1"
        max="10"
        name={name}
        value={value}
        onChange={onChange}
      />
    </div>
  );
}
