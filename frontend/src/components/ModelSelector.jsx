function ModelSelector({ model, onModelChange, lang, onLangChange }) {
  return (
    <div className="field-grid">
      <div className="field-group">
        <label htmlFor="lang-select">Ngôn ngữ</label>
        <select id="lang-select" value={lang} onChange={(event) => onLangChange(event.target.value)}>
          <option value="vi">Tiếng Việt</option>
          <option value="en">English</option>
        </select>
      </div>
      <div className="field-group">
        <label htmlFor="model-select">Model</label>
        <select id="model-select" value={model} onChange={(event) => onModelChange(event.target.value)}>
          <option value="textrank">TextRank</option>
          <option value="bilstm">BiLSTM Extractive</option>
        </select>
      </div>
    </div>
  );
}

export default ModelSelector;
