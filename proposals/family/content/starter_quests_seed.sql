-- starter_quests_seed.sql — DRAFT, not run anywhere yet.
--
-- Global starter-pack quest templates: guild_id IS NULL, per family_block.sql's
-- comment ("NULL == a global starter-pack template seeded centrally"). Run once
-- against a provisioned `dom_ai` schema, after schema/family_block.sql exists there.
-- Every family gets these by default; parents extend with their own via the
-- create_quest tool (which sets guild_id to their own family_guilds.id).
--
-- Reward numbers follow content/xp_coin_level_design.md's difficulty tiers:
--   easy = 10 xp / 10 coins, medium = 25 xp / 25 coins, hard = 50 xp / 50 coins.
-- recurrence is 'daily' or 'weekly' only here — 'once' one-off tasks don't make
-- sense as a global seed (that's what create_quest is for, per-family).
-- created_by = 'system' marks these as centrally-seeded, not parent-authored.

INSERT INTO dom_ai.quest_templates
    (guild_id, title, description, category, difficulty, xp_reward, coin_reward, recurrence, requires_proof, created_by)
VALUES
    -- homework
    (NULL, 'ทำการบ้านให้เสร็จ', 'ทำการบ้านของวันนี้ให้เรียบร้อยก่อนเข้านอน', 'homework', 'medium', 25, 25, 'daily', true, 'system'),
    (NULL, 'อ่านหนังสือ 20 นาที', 'อ่านอะไรก็ได้ที่ชอบ 20 นาที ไม่ต้องเป็นหนังสือเรียน', 'homework', 'easy', 10, 10, 'daily', false, 'system'),
    (NULL, 'ทบทวนบทเรียนก่อนสอบ', 'ทบทวนเนื้อหาที่จะสอบสัปดาห์นี้อย่างน้อยหนึ่งรอบ', 'homework', 'hard', 50, 50, 'weekly', false, 'system'),

    -- chore
    (NULL, 'เก็บที่นอนให้เรียบร้อย', 'พับผ้าห่ม จัดหมอนให้เข้าที่ทุกเช้า', 'chore', 'easy', 10, 10, 'daily', true, 'system'),
    (NULL, 'ล้างจานหลังอาหาร', 'ล้างจานของตัวเองหลังมื้ออาหารให้สะอาด', 'chore', 'easy', 10, 10, 'daily', true, 'system'),
    (NULL, 'เก็บของเล่นเข้าที่', 'เก็บของเล่นที่เล่นเสร็จแล้วกลับเข้าที่ก่อนนอน', 'chore', 'easy', 10, 10, 'daily', true, 'system'),
    (NULL, 'ทิ้งขยะ', 'เอาขยะไปทิ้งให้เรียบร้อย', 'chore', 'easy', 10, 10, 'daily', false, 'system'),
    (NULL, 'ทำความสะอาดห้องทั้งห้อง', 'จัดห้องนอนให้เรียบร้อยทั้งห้อง ไม่ใช่แค่ที่นอน', 'chore', 'hard', 50, 50, 'weekly', true, 'system'),
    (NULL, 'รดน้ำต้นไม้', 'รดน้ำต้นไม้ในบ้านให้ครบ', 'chore', 'easy', 10, 10, 'daily', false, 'system'),
    (NULL, 'พับผ้า/เก็บเสื้อผ้า', 'พับเสื้อผ้าที่ซักแล้วเก็บเข้าตู้ให้เรียบร้อย', 'chore', 'medium', 25, 25, 'weekly', true, 'system'),

    -- habit
    (NULL, 'แปรงฟันเช้า-เย็น', 'แปรงฟันให้ครบทั้งเช้าและก่อนนอน', 'habit', 'easy', 10, 10, 'daily', false, 'system'),
    (NULL, 'เข้านอนตรงเวลา', 'เข้านอนตามเวลาที่ตกลงกันไว้', 'habit', 'easy', 10, 10, 'daily', false, 'system'),
    (NULL, 'ออกกำลังกาย 15 นาที', 'ขยับร่างกายอะไรก็ได้ 15 นาที วิ่ง เต้น หรือเล่นกีฬา', 'habit', 'medium', 25, 25, 'daily', false, 'system'),
    (NULL, 'ดื่มน้ำให้ครบ', 'ดื่มน้ำให้ครบตามเป้าหมายของวันนี้', 'habit', 'easy', 10, 10, 'daily', false, 'system'),
    (NULL, 'ไม่เล่นจอก่อนนอน 1 ชม.', 'ปิดจอ (มือถือ/ทีวี/เกม) อย่างน้อย 1 ชั่วโมงก่อนเข้านอน', 'habit', 'medium', 25, 25, 'daily', false, 'system');
