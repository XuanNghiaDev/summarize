"""
generate_sample_data.py
Tạo dữ liệu mẫu hoặc tải dữ liệu thực từ VnExpress
"""
import json
import random
import os
from typing import List, Dict

VI_SAMPLES = [
    {
        "article": "Hội nghị thượng đỉnh về biến đổi khí hậu vừa kết thúc tại Geneva với sự tham gia của hơn 150 quốc gia. Các nhà lãnh đạo thế giới đã đạt được thỏa thuận lịch sử về cắt giảm khí thải carbon. Theo thỏa thuận này, các nước phát triển cam kết giảm 50% lượng khí thải vào năm 2030. Các nước đang phát triển sẽ nhận được hỗ trợ tài chính lên tới 100 tỷ đô mỗi năm. Đây được xem là bước ngoặt quan trọng trong cuộc chiến chống biến đổi khí hậu toàn cầu. Nhiều chuyên gia môi trường đánh giá cao cam kết này và kêu gọi thực thi nghiêm túc.",
        "summary": "Hội nghị thượng đỉnh Geneva đạt thỏa thuận cắt giảm 50% khí thải carbon vào 2030, các nước phát triển hỗ trợ 100 tỷ đô mỗi năm cho nước đang phát triển."
    },
    {
        "article": "Công nghệ trí tuệ nhân tạo đang thay đổi căn bản cách con người làm việc và sinh hoạt. Các mô hình ngôn ngữ lớn như GPT và Claude đã đạt được khả năng hiểu và tạo ngôn ngữ tự nhiên ở mức độ ấn tượng. Trong lĩnh vực y tế, AI đã giúp phát hiện ung thư sớm với độ chính xác cao hơn bác sĩ trong nhiều trường hợp. Giáo dục cũng đang được cách mạng hóa bởi các hệ thống học cá nhân hóa dựa trên AI. Tuy nhiên, sự phát triển nhanh chóng này cũng đặt ra nhiều lo ngại về việc làm và quyền riêng tư. Các chính phủ trên thế giới đang gấp rút xây dựng khung pháp lý để quản lý công nghệ AI.",
        "summary": "Trí tuệ nhân tạo đang cách mạng hóa y tế, giáo dục và nhiều lĩnh vực khác, nhưng cũng đặt ra lo ngại về việc làm và quyền riêng tư cần được quản lý."
    },
    {
        "article": "Thị trường bất động sản Việt Nam đang chứng kiến sự điều chỉnh mạnh sau giai đoạn tăng nóng. Giá nhà tại Hà Nội và TP.HCM đã giảm trung bình 15-20% so với đỉnh năm ngoái. Thanh khoản thị trường sụt giảm nghiêm trọng khi nhiều dự án không tìm được người mua. Ngân hàng Nhà nước đã nới lỏng một số quy định tín dụng để hỗ trợ thị trường phục hồi. Các chuyên gia dự báo thị trường sẽ tìm được đáy vào cuối năm nay và phục hồi dần từ năm sau. Người mua nhà ở thực đang có cơ hội tốt hơn để tiếp cận nhà ở với mức giá hợp lý hơn.",
        "summary": "Bất động sản Việt Nam điều chỉnh 15-20% sau giai đoạn tăng nóng, thanh khoản thấp nhưng chuyên gia dự báo phục hồi từ năm sau."
    },
    {
        "article": "Đội tuyển bóng đá Việt Nam vừa giành chiến thắng ấn tượng 3-0 trước đối thủ mạnh trong vòng loại World Cup. Tiền đạo Nguyễn Văn A ghi cú đúp trong hiệp hai quyết định trận đấu. Huấn luyện viên trưởng đánh giá cao tinh thần chiến đấu của toàn đội. Đây là chiến thắng quan trọng giúp Việt Nam leo lên vị trí thứ hai bảng đấu. Hàng triệu người hâm mộ trên khắp cả nước đã xuống đường ăn mừng chiến thắng lịch sử. Ban tổ chức FIFA cũng gửi lời chúc mừng tới đội tuyển Việt Nam sau trận đấu.",
        "summary": "Việt Nam thắng 3-0 trong vòng loại World Cup nhờ cú đúp của Nguyễn Văn A, leo lên vị trí thứ hai bảng đấu."
    },
    {
        "article": "Dịch bệnh mới xuất hiện tại một số tỉnh miền Bắc đang được cơ quan y tế theo dõi chặt chẽ. Tính đến hôm nay đã có hơn 500 ca mắc được ghi nhận với 3 ca tử vong. Bộ Y tế đã kích hoạt hệ thống ứng phó khẩn cấp và triển khai đội phản ứng nhanh đến các ổ dịch. Người dân được khuyến cáo đeo khẩu trang và hạn chế đến nơi đông người. Vaccine phòng ngừa đang được gấp rút nghiên cứu và dự kiến có thể sản xuất trong vài tháng tới. Các chuyên gia dịch tễ học đánh giá nguy cơ lây lan rộng vẫn đang ở mức thấp.",
        "summary": "Dịch bệnh mới tại miền Bắc với 500 ca mắc, Bộ Y tế kích hoạt ứng phó khẩn cấp, người dân cần đeo khẩu trang và hạn chế tụ tập."
    },
]

EN_SAMPLES = [
    {
        "article": "Scientists at MIT have developed a new battery technology that could revolutionize electric vehicles. The new solid-state battery offers three times the energy density of current lithium-ion batteries. Charging time has been reduced to just 10 minutes for a full charge. The technology eliminates the fire risks associated with liquid electrolytes. Production costs are expected to be comparable to existing batteries within five years. Several major automakers have already expressed interest in licensing the technology.",
        "summary": "MIT researchers developed solid-state batteries with 3x energy density and 10-minute charging, eliminating fire risks, with automakers showing strong interest."
    },
    {
        "article": "The global economy showed signs of recovery in the third quarter with GDP growth exceeding expectations. Inflation rates have begun to moderate in most developed economies following aggressive interest rate policies. Unemployment has fallen to pre-pandemic levels in the United States and European Union. Supply chain disruptions that plagued businesses for two years are finally easing. Consumer spending remains robust despite higher borrowing costs. Economists predict continued moderate growth through the end of the year.",
        "summary": "Global economy recovers with GDP growth above expectations, inflation moderating, unemployment at pre-pandemic lows, and supply chains normalizing."
    },
    {
        "article": "A major breakthrough in cancer treatment was announced by researchers at Johns Hopkins University. The new immunotherapy approach targets cancer stem cells that cause relapse in many patients. Clinical trials showed a 78% remission rate in patients with previously untreatable cancers. The treatment works by training the immune system to recognize and destroy cancer cells. Side effects were reported to be significantly milder than traditional chemotherapy. Regulatory approval is expected within two years if further trials confirm the results.",
        "summary": "Johns Hopkins breakthrough immunotherapy targets cancer stem cells, achieving 78% remission in untreatable cases with milder side effects than chemotherapy."
    },
]


# =========================
# TẢI DỮ LIỆU THỰC
# =========================
DATASET_FILE = "data/vnexpress_dataset.json"
CACHE_FILE = "data/vnexpress_cache.json"


def load_vnexpress_data(force_crawl: bool = False) -> List[Dict]:
    """
    Tải dữ liệu từ dataset thực hoặc cache
    
    Args:
        force_crawl: Bắt buộc crawl lại dữ liệu mới
    
    Returns:
        List of articles từ VnExpress
    """
    # Ưu tiên dùng dataset thực nếu có
    if os.path.exists(DATASET_FILE) and not force_crawl:
        try:
            with open(DATASET_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✓ Loaded {len(data)} articles from real dataset: {DATASET_FILE}")
                return data
        except Exception as e:
            print(f"⚠ Failed to load dataset file: {e}")

    # Nếu có cache và không force crawl thì dùng cache
    if os.path.exists(CACHE_FILE) and not force_crawl:
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✓ Loaded {len(data)} articles from VnExpress cache")
                return data
        except Exception as e:
            print(f"⚠ Failed to load cache: {e}")

    # Crawl dữ liệu mới
    if force_crawl:
        try:
            from crawl_vnexpress import crawl_vnexpress
            print("🚀 Crawling VnExpress data...")
            data = crawl_vnexpress(
                num_categories=2,
                articles_per_category=10,
                use_cache=False,
                delay=1.0
            )
            if data:
                os.makedirs("data", exist_ok=True)
                try:
                    with open(DATASET_FILE, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"✓ Saved {len(data)} articles to real dataset: {DATASET_FILE}")
                except Exception as e:
                    print(f"⚠ Failed to save dataset file: {e}")
            return data
        except Exception as e:
            print(f"✗ Crawling failed: {e}")
            return []

    return []


def process_vnexpress_data(data: List[Dict], n_samples: int = 200) -> List[Dict]:
    """
    Chuyển đổi dữ liệu VnExpress thành format phù hợp
    
    Args:
        data: Raw data từ VnExpress scraper
        n_samples: Số lượng samples cần (nếu ít hơn sẽ repeat)
    
    Returns:
        Processed data ready for training
    """
    if not data:
        return []
    
    processed = []
    for i in range(n_samples):
        base = data[i % len(data)]
        processed.append({
            "id": f"vi_{i:04d}",
            "article": base.get("article", ""),
            "summary": base.get("summary", ""),
            "url": base.get("url", ""),
            "lang": "vi"
        })
    
    return processed


def generate(n_vi=200, n_en=200, use_real_data: bool = False, force_crawl: bool = False):
    """
    Tạo dữ liệu cho training
    
    Args:
        n_vi: Số mẫu tiếng Việt
        n_en: Số mẫu tiếng Anh
        use_real_data: Dùng dữ liệu thực từ VnExpress
        force_crawl: Bắt buộc crawl dữ liệu mới
    """
    # =========================
    # TIẾNG VIỆT
    # =========================
    real_data_used = False
    if use_real_data:
        print("\n📡 Loading real Vietnamese data from VnExpress...")
        vnexpress_data = load_vnexpress_data(force_crawl=force_crawl)
        if vnexpress_data:
            vi_data = process_vnexpress_data(vnexpress_data, n_vi)
            print(f"✓ Loaded {len(vi_data)} real Vietnamese articles")
            real_data_used = True
        else:
            print("⚠ No real data available, using samples")
            vi_data = []
            for i in range(n_vi):
                base = VI_SAMPLES[i % len(VI_SAMPLES)]
                vi_data.append({
                    "id": f"vi_{i:04d}",
                    "article": base["article"],
                    "summary": base["summary"],
                    "lang": "vi"
                })
    else:
        vi_data = []
        for i in range(n_vi):
            base = VI_SAMPLES[i % len(VI_SAMPLES)]
            vi_data.append({
                "id": f"vi_{i:04d}",
                "article": base["article"],
                "summary": base["summary"],
                "lang": "vi"
            })
    
    # =========================
    # TIẾNG ANH
    # =========================
    en_data = []
    for i in range(n_en):
        base = EN_SAMPLES[i % len(EN_SAMPLES)]
        en_data.append({
            "id": f"en_{i:04d}",
            "article": base["article"],
            "summary": base["summary"],
            "lang": "en"
        })
    
    # =========================
    # SAVE JSON
    # =========================
    os.makedirs("data", exist_ok=True)

    if not use_real_data or not real_data_used:
        with open("data/sample_vi.json", "w", encoding="utf-8") as f:
            json.dump(vi_data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Tạo {len(vi_data)} mẫu tiếng Việt → data/sample_vi.json")
    else:
        print("[OK] Đã dùng dữ liệu thật, không tạo sample_vi.json")
    
    with open("data/sample_en.json", "w", encoding="utf-8") as f:
        json.dump(en_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Tạo {len(en_data)} mẫu tiếng Anh  → data/sample_en.json")


if __name__ == "__main__":
    generate()
