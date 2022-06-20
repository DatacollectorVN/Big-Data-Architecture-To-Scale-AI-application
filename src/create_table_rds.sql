-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema x_ray
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema x_ray
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `x_ray` DEFAULT CHARACTER SET utf8 ;
-- -----------------------------------------------------
-- Schema x_ray
-- -----------------------------------------------------
USE `x_ray` ;

-- -----------------------------------------------------
-- Table `mydb`.`image`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `x_ray`.`image` (
  `image_id` INT NOT NULL,
  `bucket` VARCHAR(100) NOT NULL,
  `folder` VARCHAR(100) NOT NULL,
  `image_file` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`image_id`),
  UNIQUE INDEX `image_id_UNIQUE` (`image_id` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`transaction`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `x_ray`.`transaction` (
  `transaction_id` INT NOT NULL,
  `image_id` INT NOT NULL,
  `time` DATETIME NOT NULL,
  `cs_thr` DECIMAL(4,3) NOT NULL,
  `nms_thr` DECIMAL(4,3) NOT NULL,
  PRIMARY KEY (`transaction_id`, `image_id`),
  UNIQUE INDEX `transaction_d_UNIQUE` (`transaction_id` ASC) VISIBLE,
  UNIQUE INDEX `time_UNIQUE` (`time` ASC) VISIBLE,
  INDEX `fk_transaction_image_idx` (`image_id` ASC) VISIBLE,
  CONSTRAINT `fk_transaction_image`
    FOREIGN KEY (`image_id`)
    REFERENCES `mydb`.`image` (`image_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`pred_bounding_box`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `x_ray`.`pred_bounding_box` (
  `pred_bbox_id` INT NOT NULL,
  `transaction_id` INT NOT NULL,
  `pred_class` INT NOT NULL,
  `pred_cs` DECIMAL(4,3) NOT NULL,
  `x_min` INT NOT NULL,
  `y_min` INT NOT NULL,
  `x_max` INT NOT NULL,
  `y_max` INT NOT NULL,
  PRIMARY KEY (`pred_bbox_id`, `transaction_id`),
  UNIQUE INDEX `pred_bbox_id_UNIQUE` (`pred_bbox_id` ASC) VISIBLE,
  INDEX `fk_pred_bounding_box_transaction1_idx` (`transaction_id` ASC) VISIBLE,
  CONSTRAINT `fk_pred_bounding_box_transaction1`
    FOREIGN KEY (`transaction_id`)
    REFERENCES `mydb`.`transaction` (`transaction_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;