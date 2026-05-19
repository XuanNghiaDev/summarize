function RougeScore({ rouge }) {
  if (!rouge) {
    return null;
  }

  return (
    <div className="rouge-grid">
      <div className="badge">ROUGE-1: {rouge.rouge1?.toFixed(3) ?? 'N/A'}</div>
      <div className="badge">ROUGE-2: {rouge.rouge2?.toFixed(3) ?? 'N/A'}</div>
      <div className="badge">ROUGE-L: {rouge.rougeL?.toFixed(3) ?? 'N/A'}</div>
    </div>
  );
}

export default RougeScore;
