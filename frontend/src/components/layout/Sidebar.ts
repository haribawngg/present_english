import { icon } from '../../utils/icons';
export function sidebarTemplate(): string {
    return `<aside class="sidebar"><a class="brand" href="#"><span class="brand-icon">${icon('shield')}</span> SMS<span class="brand-light">Lab</span></a>
<div class="workspace-label">MACHINE LEARNING WORKSPACE</div>
<nav aria-label="Điều hướng"><button class="nav active" data-view="classify">${icon('message')} <span>Phân loại tin nhắn</span></button><button class="nav" data-view="evaluation">${icon('chart')} <span>Đánh giá mô hình</span></button></nav>
<div class="sidebar-note"><span class="tiny">BÀI THỰC HÀNH NLP</span><h3>Từ dữ liệu đến dự đoán.</h3><p>Khám phá cách các mô hình học máy nhận diện tin nhắn rác.</p><span class="version">SMS Spam Collection <span>v1.0</span></span></div>
<div class="sidebar-footer"><span class="avatar">ML</span><div>Classification Lab<small>Demo học máy</small></div></div></aside>
`;
}
