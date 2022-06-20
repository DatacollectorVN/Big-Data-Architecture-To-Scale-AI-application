USE x_ray;
SET FOREIGN_KEY_CHECKS=0;
INSERT INTO transaction VALUES (1, 1,  '2022-05-24 11:08:23', 0.3, 0.5);
INSERT INTO transaction VALUES (2, 2, '2022-05-24 11:09:30',  0.3, 0.5);
INSERT INTO pred_bounding_box VALUES (1, 1, 3, 0.5, 611, 184, 757, 272);
INSERT INTO pred_bounding_box VALUES (2, 1, 3, 0.39, 583, 168, 767, 348);
INSERT INTO pred_bounding_box VALUES (3, 2,	2, 0.5, 611, 200, 700, 272);
INSERT INTO pred_bounding_box VALUES (4, 2, 2, 0.7, 600, 200, 720, 350);
INSERT INTO pred_bounding_box VALUES (5, 2,	3, 0.39, 584, 170, 760, 348);
INSERT INTO image VALUES (1, 'nhannt70', 'xray-images', 'img_1');
INSERT INTO image VALUES (2, 'nhannt70', 'xray-images', 'img_1');

