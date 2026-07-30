DRAFT — copy/paste into LINE, Slack, or email to whoever owns the Duply platform code.

---

เปิด PR ไว้แล้วนะ: เสนอ archetype ใหม่ "family" สำหรับบอทตัวหนึ่งที่อยากลองทำ — ชื่อ Dom, เป็นบอทที่ช่วยผู้ปกครองดูแลลูกๆ เรื่อง routine ประจำวัน ให้เควส (การบ้าน/งานบ้าน/นิสัยดีๆ) เก็บ XP/เหรียญ มีเลเวล มีแรงกิ้งทั้งในครอบครัวและ global ด้วย

PR: https://github.com/duplyofficial-thay/duply-creator/pull/1

ในนั้นมีครบแล้ว: SQL schema ใหม่ 11 ตาราง, tool ใหม่ 15 ตัว, การ์ด LINE เต็มระบบ (ไม่ใช่ stub), ระบบเตือนตามตารางเวลาแบบใหม่ (schedule.nudge), และ diff ที่ต้องแก้ใน provision_duple.py แบบระบุบรรทัดชัดเจนแล้ว (ดูใน platform_changes/provision_duple_notes.md)

สิ่งที่อยากให้ช่วยดู:
1. เช็คว่า approach การเพิ่ม archetype ใหม่แบบนี้โอเคไหม หรืออยากให้ทำต่างไป
2. คำถามที่ยังค้างอยู่ (สำคัญสุด) — postback_routes ที่ใช้ตอนนี้ (ของ khun) ดูเหมือนจะแค่ re-render การ์ดตอนกดปุ่ม แต่ระบบของ Dom ต้องการให้พ่อแม่กด Approve/Reject บนการ์ดแล้วเขียนลง DB จริงๆ (อนุมัติงานที่ลูกส่งมา) — อันนี้ postback_routes รองรับได้เลยไหม หรือต้องทำอีกแบบ?
3. เรื่อง photo storage สำหรับรูปหลักฐานที่เด็กส่งมา (ยังไม่มีระบบเก็บไฟล์ใน platform ตอนนี้เลย) — อยากรู้ว่าพอจะประเมินได้ไหมว่าใหญ่แค่ไหน

ยังไม่ merge ไม่ provision อะไรทั้งนั้น รอฟังความเห็นก่อน ว่างเมื่อไหร่ลองดูให้หน่อยได้มั้ย
