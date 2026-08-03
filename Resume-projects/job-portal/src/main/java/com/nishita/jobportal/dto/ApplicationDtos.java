package com.nishita.jobportal.dto;
import com.nishita.jobportal.entity.*;
import jakarta.validation.constraints.*;
import java.time.Instant;
public final class ApplicationDtos {
 private ApplicationDtos(){}
 public record ApplyRequest(@NotNull Long jobId,@Size(max=2000) String coverNote){}
 public record StatusRequest(@NotNull ApplicationStatus status){}
 public record ApplicationResponse(Long id,Long jobId,String jobTitle,String company,Long candidateId,String candidateName,String candidateEmail,ApplicationStatus status,Instant appliedAt){
  public static ApplicationResponse from(JobApplication a){return new ApplicationResponse(a.getId(),a.getJob().getId(),a.getJob().getTitle(),a.getJob().getCompany().getName(),a.getCandidate().getId(),a.getCandidate().getName(),a.getCandidate().getEmail(),a.getStatus(),a.getAppliedAt());}
 }
}
