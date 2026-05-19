function About() {
  return (
    <section className="page-about">
      <div className="card card-panel">
        <h2>Giới thiệu hệ thống</h2>
        <p>
          Web Edition của hệ thống tóm tắt văn bản. Backend Express gọi tới Flask AI Core,
          frontend React/Vite hiển thị kết quả ngay lập tức.
        </p>
        <ul>
          <li>Model: TextRank, BiLSTM Extractive, Seq2Seq Abstractive</li>
          <li>Ngôn ngữ: Tiếng Việt và Tiếng Anh</li>
          <li>Local deployment: React + Express + Python</li>
        </ul>
      </div>
    </section>
  );
}

export default About;
