export function pipelineTemplate(): string {
    return `<section class="pipeline"><div><span class="eyebrow">QUY TRÌNH XỬ LÝ</span><h3>Từ văn bản đến nhãn phân loại</h3></div><div class="pipeline-steps"><span>01 <b>Chuẩn hóa</b><small>NLTK · lemma + stem</small></span><i>→</i><span>02 <b>Biểu diễn</b><small>Vocabulary từ tập train</small></span><i>→</i><span>03 <b>Dự đoán</b><small>Ham hoặc spam</small></span></div></section>`;
}
