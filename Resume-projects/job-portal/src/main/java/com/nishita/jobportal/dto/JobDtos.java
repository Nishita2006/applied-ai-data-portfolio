package com.nishita.jobportal.dto;
import com.nishita.jobportal.entity.*;
import jakarta.validation.constraints.*;
import java.time.Instant;
public final class JobDtos {
 private JobDtos(){}
 public record JobRequest(@NotNull Long companyId,@NotBlank String title,@NotBlank @Size(max=4000) String description,@NotBlank String location,@NotBlank String employmentType,@NotBlank String skills,@PositiveOrZero Integer salaryMin,@PositiveOrZero Integer salaryMax){}
 public record JobResponse(Long id,String title,String company,String location,String employmentType,String skills,Integer salaryMin,Integer salaryMax,JobStatus status,String description,Instant createdAt){
  public static JobResponse from(JobPosting j){return new JobResponse(j.getId(),j.getTitle(),j.getCompany().getName(),j.getLocation(),j.getEmploymentType(),j.getSkills(),j.getSalaryMin(),j.getSalaryMax(),j.getStatus(),j.getDescription(),j.getCreatedAt());}
 }
}
